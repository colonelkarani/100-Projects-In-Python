from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get("https://www.tuko.co.ke/kenya/")

wait = WebDriverWait(driver, 10)
news = wait.until(EC.presence_of_all_elements_located(
    (By.CLASS_NAME, "top-articles-popular__headline--hover-inner")
))

data = [[item.text] for item in news]
filename = 'news.csv'
index= 0
while index < len(data):
    new_row = data[index]
    # Step 1: Read existing rows into a set
    with open(filename, newline='') as csvfile:
     reader = csv.reader(csvfile)
     existing_rows = set(tuple(row) for row in reader)

    # Step 2: Check if the new row is a duplicate
    if tuple(new_row) not in existing_rows:
    # Step 3: Append the new row if it's unique
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(new_row)
            print("Row written.")
    else:
        print("Duplicate row detected, not writing.")
    index+= 1

driver.quit() 
