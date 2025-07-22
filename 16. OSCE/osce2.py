import os
import pandas as pd
import random
import cv2
import requests
import json
import tempfile
from dotenv import load_dotenv
from selenium import webdriver
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                      'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                      'Chrome/117.0.0.0 Safari/537.36'
}


load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    print("Warning: No API_KEY found in environment variables. AI explanations will not work.")

# Download image from URL to a temporary file and return the filepath
def download_image(url):
    try:
        resp = requests.get(url, stream=True, headers=HEADERS,timeout=10)
        resp.raise_for_status()
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        for chunk in resp.iter_content(1024):
            tmp_file.write(chunk)
        tmp_file.close()
        return tmp_file.name
    except Exception as e:
        print(f"Failed to download image {url}: {e}")
        return None

def show_image(image_path):
    if not image_path or not os.path.exists(image_path):
        print("Image not available to display.")
        return
    img = cv2.imread(image_path)
    if img is None:
        print("Failed to load image for display.")
        return
    cv2.imshow("OSCE Pictorial Question - Press any key to continue", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # Remove temp file to avoid clutter
    if image_path.startswith(tempfile.gettempdir()):
        os.remove(image_path)


def show_pic(url):
    driver = webdriver.Chrome()

    try:
        driver.get(url)
        driver.fullscreen_window()
        time.sleep(15)
    finally:
        driver.quit()
        


def get_topics():
    path = "./csv"
    if not os.path.exists(path):
        print("No ./csv directory found with question files.")
        return []
    topics = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return topics

def get_files(folder):
    folder_path = f"./csv/{folder}"
    if not os.path.exists(folder_path):
        return []
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.csv')]
    return files

def load_questions(csv_path):
    try:
        df = pd.read_csv(csv_path)
        # Filter rows with all required columns non-null
        required_cols = ['Image', 'Description', 'Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer']
        df = df.dropna(subset=required_cols)
        valid_idx = df.index.tolist()
        if len(valid_idx) == 0:
            raise ValueError("No valid questions found in the CSV file.")
        return df, valid_idx
    except Exception as e:
        print(f"Failed to load or parse CSV: {e}")
        raise

def quiz_loop(df, valid_idx, num_questions, csv_path):
    passed = 0
    streak = 0
    highest_streak = 0
    failed = []

    selected_indices = random.sample(valid_idx, num_questions)

    for idx in selected_indices:
        row = df.loc[idx]
        #row = df.loc[1]
        print("\n" + "="*50)
        #print(f"Description:\n{row['Description']}\n")
        # img_path = download_image(row['Image'])
        # show_image(img_path)
        show_pic(row["Image"])

        print(f"Question:\n{row['Question']}\n")
        options = {
            'A': row['Option A'],
            'B': row['Option B'],
            'C': row['Option C'],
            'D': row['Option D'],
        }
        for letter, text in options.items():
            print(f"{letter}: {text}")
        
        correct_answer = row['Correct Answer']

        user_answer_text = None
        while True:
            answer = input("\nYour answer (A/B/C/D) or type 'delete' to remove this question: ").strip().upper()
            if answer == 'DELETE':
                # Delete question from df and save
                df.drop(idx, inplace=True)
                df.to_csv(csv_path, index=False)
                print("*** Question deleted from dataset ***")
                user_answer_text = None
                break
            elif answer in ['A','B','C','D']:
                user_answer_text = options[answer]
                break
            else:
                print("Invalid input. Please enter A, B, C, D, or 'delete'.")

        if user_answer_text is None:
            # Question deleted, skip scoring
            continue

        if user_answer_text == correct_answer:
            passed += 1
            streak += 1
            highest_streak = max(highest_streak, streak)
            print(f"\033[92mCorrect! (Streak: {'🔥'*streak})\033[0m")
        else:
            print(f"\033[91mIncorrect. Correct answer: {correct_answer}\033[0m")
            streak = 0
            failed.append({
                'question': row['Question'],
                'user_answer': user_answer_text,
                'correct_answer': correct_answer,
                'description': row['Description'],
                'image_url': row['Image'],
                'choices': options
            })

    return passed, highest_streak, failed

def explain_incorrect_questions(failed):
    if not api_key:
        print("\nNo API key available; skipping AI explanations.")
        return

    print("\n" + "="*50)
    print("Explanation for missed questions:\n")
    for idx, f in enumerate(failed, 1):
        print("-"*50)
        print(f"Question {idx}:\n{f['question']}")
        print(f"Your answer: \033[91m{f['user_answer']}\033[0m")
        print(f"Correct answer: \033[92m{f['correct_answer']}\033[0m")
        print(f"Description: {f['description']}")
        img_path = download_image(f['image_url'])
        show_image(img_path)

        prompt = (
            "Explain why the correct answer is right and why the user's answer is wrong "
            f"for this medical OSCE question: '{f['question']}'. "
            f"Correct answer: {f['correct_answer']}. "
            f"User's answer: {f['user_answer']}. "
            "Provide a concise medical explanation in plain text only."
        )

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": api_key,
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "model": "deepseek/deepseek-chat-v3-0324:free",
                    "messages": [{"role": "user", "content": prompt}]
                }),
                timeout=15
            )
            if response.status_code == 200:
                explanation = response.json()['choices'][0]['message']['content']
                print(f"\nAI Explanation:\n{explanation}")
            else:
                print(f"Failed to get AI explanation: status {response.status_code}")
        except Exception as e:
            print(f"Exception while calling AI: {e}")
        
        input("\nPress Enter to continue to the next explanation...")

if __name__ == "__main__":
    print("Welcome to the OSCE Pictorial Quiz App!\n")

    topics = get_topics()
    if not topics:
        print("No topics found in ./csv folder. Please create folders with CSV files as per instructions.")
        exit()

    print("Available Topics:\n" + "\n".join(topics))
    topic = input("Enter the topic you want to study today: ").strip()
    if topic not in topics:
        print("Invalid topic selection.")
        exit()

    files = get_files(topic)
    if not files:
        print(f"No CSV files found in topic folder './csv/{topic}'.")
        exit()

    print("\nAvailable files:\n" + "\n".join(files))
    csv_file = input("Enter the filename you want to study: ").strip()
    if csv_file not in files:
        print("Invalid file selection.")
        exit()

    csv_path = f"./csv/{topic}/{csv_file}"
    try:
        df, valid_indices = load_questions(csv_path)
    except Exception as e:
        print(f"Error loading questions: {e}")
        exit()

    max_q = len(valid_indices)
    while True:
        try:
            n = int(input(f"How many questions would you like to answer? (1-{max_q}): "))
            if 1 <= n <= max_q:
                break
            print(f"Please enter a number between 1 and {max_q}")
        except ValueError:
            print("Invalid input. Enter a number.")

    correct_count, best_streak, failed_questions = quiz_loop(df, valid_indices, n, csv_path)

    print("\n" + "="*50)
    print(f"Quiz complete! Your score: {correct_count}/{n} ({round(correct_count/n*100)}%)")
    print(f"Highest Streak: {best_streak}")

    if failed_questions:
        explain_incorrect_questions(failed_questions)
    else:
        print("Amazing! You got all questions right!")

    print("\nThank you for using the OSCE Pictorial Quiz App.")
