
import pandas as pd
import requests
import random
df = pd.read_csv("anti-dm.csv")


number_of_questions =  int(input("How many questions do you want to learn today?  ------>   "))

passed = 0
streak = 0
failed = 0
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
        failed += 1
        streak = 0
        print(f"Too Bad\n The Answer is Wrong,\n the correct answer is {ans}\n")

if(passed == number_of_questions):
    print("Are you sure you are not a genius or something 🤔🤔 ")

score = round(passed/number_of_questions, 2)

print(f"You got {score}% right\n")
print("\033[34m-\033[0m"*passed*10 + "\033[33m-\033[0m"*failed*10)

 




    



