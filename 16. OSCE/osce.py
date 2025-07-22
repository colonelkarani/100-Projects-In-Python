import os
import pandas as pd
import random
import cv2
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

def get_topics():
    topics = os.listdir("./csv")
    return "\n".join(topics)

def get_files(folder):
    files = os.listdir(f"./csv/{folder}")
    return "\n".join(files)

def show_image(image_path):
    # Load image using OpenCV and show it
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not open image: {image_path}")
        return
    cv2.imshow("OSCE Pictorial Question", img)
    print("Image window opened. Press any key on the image window to continue...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def load_questions(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except pd.errors.ParserError:
        df = pd.read_csv(csv_path, on_bad_lines='skip', engine='python')
    # Filter out rows with nulls in critical columns
    valid_idx = [i for i in range(len(df)) if not df.loc[i, ['Image','Description','Question','Option A','Option B','Option C','Option D','Correct Answer']].isnull().any()]
    if len(valid_idx) == 0:
        raise ValueError("No valid questions found in this dataset.")
    return df, valid_idx

def quiz(df, valid_idx, num_questions):
    passed = 0
    streak = 0
    highest_streak = 0
    failed = []

    selected_indices = random.sample(valid_idx, num_questions)

    for idx in selected_indices:
        row = df.loc[idx]
        image_path = row['Image']
        description = row['Description']
        question = row['Question']
        options = {
            'A': row['Option A'],
            'B': row['Option B'],
            'C': row['Option C'],
            'D': row['Option D']
        }
        correct_ans = row['Correct Answer']

        print("\n" + "="*50)
        show_image(image_path)
        print(f"\nQuestion: {question}")
        for letter, text in options.items():
            print(f"{letter}: {text}")

        while True:
            user_input = input("Your answer (A/B/C/D) or type 'delete' to remove this question:\n").strip().upper()
            if user_input == "DELETE":
                df.drop(idx, inplace=True)
                df.to_csv(csv_path, index=False)
                print("*** Question deleted from database ***")
                user_answer = None
                break
            if user_input in ['A','B','C','D']:
                user_answer = options[user_input]
                break
            print("Invalid input. Please enter A, B, C, D or 'delete'.")

        if user_answer is None:
            # Question deleted, skip scoring
            continue

        if user_answer == correct_ans:
            passed += 1
            streak += 1
            highest_streak = max(highest_streak, streak)
            print(f"\033[92mCorrect! (Streak: {'🔥'*streak})\033[0m")
        else:
            failed.append({
                'question': question,
                'user_answer': user_answer,
                'correct_answer': correct_ans,
                'description': description,
                'image_path': image_path,
                'choices': options
            })
            streak = 0
            print(f"\033[91mIncorrect. Correct answer: {correct_ans}\033[0m")

    return passed, highest_streak, failed

def explain_fails(failed):
    print("\n" + "="*50)
    print("Explanation for incorrectly answered questions\n")

    for f in failed:
        print("-"*50)
        print(f"Question: {f['question']}")
        print(f"Your answer: \033[91m{f['user_answer']}\033[0m")
        print(f"Correct answer: \033[92m{f['correct_answer']}\033[0m")
        print(f"Description: {f['description']}")
        show_image(f['image_path'])
        prompt = (
            "Explain why the correct answer is right and why the user's answer is wrong "
            f"for this medical OSCE question: '{f['question']}'. "
            f"Correct answer: {f['correct_answer']}. "
            f"User's answer: {f['user_answer']}. "
            "Provide a concise medical explanation in plain text only."
        )
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        if response.status_code == 200:
            explanation = response.json()['choices'][0]['message']['content']
            print(f"\nAI Explanation:\n{explanation}")
        else:
            print(f"\nError getting explanation (Status {response.status_code})")

        input("\nPress Enter to continue...\n")

if __name__ == "__main__":
    print("Welcome to the OSCE Pictorial Quiz!\n")
    topic = input(f"What topic do you want to learn today?\nAvailable topics:\n{get_topics()}\n\n")
    csv_file = input(f"\nWhich file do you want to study?\nAvailable files:\n{get_files(topic)}\n\n")

    csv_path = f"./csv/{topic}/{csv_file}"
    try:
        df, valid_idx = load_questions(csv_path)
    except Exception as e:
        print(f"Error loading questions: {e}")
        exit()

    max_questions = len(valid_idx)
    while True:
        try:
            n = int(input(f"How many questions do you want? (1-{max_questions}): "))
            if 1 <= n <= max_questions:
                break
            else:
                print(f"Enter a number between 1 and {max_questions}")
        except ValueError:
            print("Please enter a valid number.")

    score, best_streak, failed_qs = quiz(df, valid_idx, n)

    print("\n" + "="*50)
    print(f"Quiz Finished! Score: {score}/{n} ({round(score/n*100)}%)")
    print(f"Best Streak: {best_streak}\n")

    if failed_qs:
        explain_fails(failed_qs)
    else:
        print("Congratulations! You got all questions right!")

