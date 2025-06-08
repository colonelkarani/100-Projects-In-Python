# there is a prefix number set try to guess it within the tries  allocated, 
# if you guess a number i will tell you if its higher or lower
# guess more than 7 numbers and the liimit is gone 
# a high score is stored in a separate csv file with the and the 
# high score is updated when the user sets a new high score,   

import time
import sys
import random
import csv
import os

LEADERBOARD_FILE = 'leaderboard.csv'

def update_leaderboard(name, tries):
    # Check if the file exists, if not, create it with headers
    file_exists = os.path.isfile(LEADERBOARD_FILE)
    with open(LEADERBOARD_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['name', 'tries'])
        writer.writerow([name, tries])
def get_leaderboard():
    leaderboard = []
    if os.path.isfile(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                leaderboard.append({'name': row['name'], 'tries': int(row['tries'])})
        # Sort by tries (ascending: lower is better)
        leaderboard = sorted(leaderboard, key=lambda x: x['tries'])
    return leaderboard
def show_leaderboard(current_name, current_tries):
    leaderboard = get_leaderboard()
    print("\n🏅 Leaderboard 🏅")
    print("Place | Name       | Tries")
    print("-------------------------------")
    your_place = None
    for i, entry in enumerate(leaderboard, start=1):
        line = f"{i:5} | {entry['name']:<10} | {entry['tries']}"
        if entry['name'] == current_name and entry['tries'] == current_tries and your_place is None:
            line += "   <== You!"
            your_place = i
        print(line)
    if your_place:
        print(f"\n🎉 {current_name}, you are #{your_place} on the leaderboard!")
    else:
        print("\nYour score was not found on the leaderboard (did you enter a new name each time?)")


name = input(" please enter you name: ")
def  game(num, comp_random, count = 0):
     
     if num < comp_random: 
        othernumber = int(input(" the number you entered is too low please try again:   "))
        count += 1
        game(othernumber, comp_random, count)
     elif num > comp_random: 
        othernumber = int(input(" the number you entered is too high please try again:  "))
        count +=1
        game(othernumber, comp_random, count)
     else:
        print(f"🍾🍾🍾🍾🍾 you won {name}  congratulations🍾🍾🍾🍾🍾")
        print(f"You finished the game in {count} tries")
        # When player wins:
        update_leaderboard(name, count)
        show_leaderboard(name, count)

print(f"hello {name} today we are going to play a game")
time.sleep(1)
print('Are you ready?')
time.sleep(1)

ready = input(" Just say yes or no  ---->")
if ready.lower() == 'yes':
    print('Okay lets start')
    time.sleep(1)
    print("we are going to play a number guessing game")
    time.sleep(1)
    print("You'll guess a number and I'll tell you if it's  close to my number ")
    time.sleep(2)
    number_string = input("guess a number between 0 to 100.  0 and 100 included😊---->")
    try:
        number = int(number_string)
    except ValueError:
        print(f"please input a number is like 69 not {number_string}")
    comp_random = random.randint(0, 100)
    game(number,  comp_random, 1)
elif ready.lower() == 'no':
    print("too bad it's bye for now")
else:
    print("you haven't understood i told you to only say yes or no")
    sys.exit()




