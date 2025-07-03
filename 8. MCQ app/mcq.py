import os
import pandas as pd
import json
import requests
import random
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

def get_topics():
    topics = os.listdir("./csv")
    return "\n".join(topics)

def get_files(folder):
    files = os.listdir("./csv/" + folder)
    return "\n".join(files)

folder = input(f"What topic do you want to learn today? \nAvailable topics:   \n{get_topics()}\n")
file = input(f"\n\nWhat files do you want to study today? \nAvailable files:   \n{get_files(folder)}\n   ")
# Read CSV file with error handling
try:
    df = pd.read_csv("./csv/"+ folder+"/"+file)
except pd.errors.ParserError:
    df = pd.read_csv("./csv/"+folder +"/"+file, on_bad_lines='skip', engine='python')

# Ensure we have enough valid questions
valid_indices = [i for i in range(len(df)) if not df.iloc[i].isnull().any()]
total_questions = len(valid_indices)

if total_questions == 0:
    print("Error: No valid questions found in the dataset!")
    exit()

# Get user input with validation
while True:
    try:
        number_of_questions = int(input("How many questions do you want to learn today? \n"))
        if 1 <= number_of_questions <= total_questions:
            break
        print(f"Please enter a number between 1 and {total_questions}")
    except ValueError:
        print("Invalid input. Please enter a number.")

def ask_questions():
    passed = 0
    streak = 0
    highest_streak = 0
    failed = []
    try:
        while True:
            try:
                selected_indices = random.sample(valid_indices, number_of_questions)
                break
            except IndexError:
                print("Index out of bounds error. Retrying selection...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit()

    try:
        for idx in selected_indices:
            row = df.iloc[idx]
            question = row.Question
            choices = {
                'A': row["Option A"],
                'B': row["Option B"],
                'C': row["Option C"],
                'D': row["Option D"]
            }
            ans = row["Correct Answer"]

            print(f"\n{question}")
            for letter, option in choices.items():
                print(f"{letter}: {option}")

            while True:
                user_letter = input("What's your answer? (A/B/C/D)\nType delete to delete this question\n ").upper().strip()
                if user_letter == "DELETE":
                    df.drop(idx, inplace=True)
                    df.to_csv("./csv/"+ folder+"/"+file, index=False)
                    print("Question deleted")
                    user_answer = 0
                    break
                elif user_letter in choices:
                    user_answer = choices[user_letter]
                    break
                print("Invalid choice. Please enter A, B, C, or D.")

            if user_answer == 0:
                continue
            elif user_answer == ans:
                passed += 1
                streak += 1
                highest_streak = max(highest_streak, streak)
                print(f"\n✅ Correct! (Streak: {'🔥' * streak})")
            else:
                failed.append({
                    'question': question,
                    'user_answer': user_answer,
                    'correct_answer': ans,
                    'choices': choices
                })
                streak = 0
                print(f"\n❌ Incorrect. The correct answer is: {ans}")

    except KeyboardInterrupt:
        print("\n\nQuiz interrupted by user.")
        print(f"\n{'='*50}")
        print(f"Points accumulated: {passed}")
        print(f"Questions attempted: {passed + len(failed)}")
        print(f"Highest streak: {highest_streak}")
        exit()

    score = round(passed / number_of_questions * 100)
    print(f"\n{'='*50}")
    print(f"Final Score: {score}% ({passed}/{number_of_questions})")
    print(f" <{'\033[32m■\033[0m' * passed*5}{'\033[31m■\033[0m' * (number_of_questions - passed)*5}>")
    print(f"Highest streak: {highest_streak}")

    if passed == number_of_questions:
        print("🌟 Are you sure you're not a genius? 🌟")

    # Explanation for failed questions
    for f in failed:
        print("\n" + "="*50)
        print(f"Explanation for missed question:\n{f['question']}")
        print(f"\nYour answer: \033[31m{f['user_answer']}\033[0m")
        print(f"Correct answer: \033[32m{f['correct_answer']}\033[0m")
        
        # API request for explanation
        prompt = (
            "Explain why the correct answer is right and why the user's answer is wrong "
            f"for this medical question: '{f['question']}'. "
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
            print(f"\nExplanation:\n{explanation}")
            cont = input("\nPress Enter to check next question\n")
        else:
            print(f"\nError getting explanation (Status {response.status_code})")

ask_questions()
