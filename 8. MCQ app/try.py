import os
import pandas as pd
import json
import requests
import random
from dotenv import load_dotenv
load_dotenv()
#print(os.listdir("./"))


api_key = os.getenv("API_KEY")

df = pd.read_csv("stroke.csv")

number_of_questions =  int(input("How many questions do you want to learn today?  ------>   "))

passed = 0
streak = 0
failed = []
for i in range(number_of_questions):
    randomint = random.randint(1, df.Question.count())
    question = df.iloc[randomint].Question
    choice_a = df.iloc[randomint]["Option A"]
    choice_b = df.iloc[randomint]["Option B"]
    choice_c = df.iloc[randomint]["Option C"]
    choice_d = df.iloc[randomint]["Option D"]

    choices = [choice_a, choice_b, choice_c, choice_d]
    ans = df.iloc[randomint]["Correct Answer"]

    print(question)
    print(f"A:  {choice_a}")
    print(f"B:  {choice_b}")
    print(f"C:  {choice_c}")
    print(f"D:  {choice_d}")
    


    user_answer = df.iloc[randomint]["Option "+ input("Whats your answer?  ").upper()]
    if user_answer == ans:
        passed += 1
        streak +=1
        print(f"You Got {passed} questions right\n Streak: {"🔥"* streak}\n")
    else:
        failed.append([question, user_answer, choices])
        streak = 0
        print(f"Too Bad\n The Answer is Wrong,\n the correct answer is {ans}\n")

if(passed == number_of_questions):
    print("Are you sure you are not a genius or something 🤔🤔 ")

score = round(passed/number_of_questions, 2)*100

print(f"You got {score}% right\n")
print("<"+"\033[32m---\033[0m"*score+"\033[36m---\033[0m"*(100 - score)+">")

for f in failed:
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": api_key,
        "Content-Type": "application/json",
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
        {
            "role": "user",
            "content": "You are a messaging bot from the terminal, please output only plain text, here is the message from the user: Do not format this is not an md document, !!!only text  DO NOT USE MARKDOWN FORMATTERS"+ "help a medical student to revise these are the failed questions adn explain why he failed why that is the answer and why it is relevant. This is the question and answer and choices. output only why answer is correct . REMEMBER ONLY PLAIN TEXT"+ str(f)
        }
        ],
    })
    )
    if response.status_code == 200:
    # Parse the JSON response
        response_data = response.json()  # This will convert the response to a Python dictionary

        if 'choices' in response_data:
            answer = response_data['choices'][0]['message']['content']
        
            print(f"You failed ::::{str(f[0])}\n Your answer:::::: \033[31m{str(f[1])}\033[0m\n Heres Why ---::", answer, "")
    else:
        print("Error:", response.status_code, response.text)









        