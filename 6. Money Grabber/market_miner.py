from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

driver.get("https://www.tradingview.com/news/")

# Try using class name or XPath if ID doesn't work
headlines = driver.find_elements(By.XPATH, '//*[@id= "news_top_stories"]/div/div/div/div/a/article/div/div')

print("")
if headlines:
    for headline in headlines:
        with open("news.txt", "a") as f:
            f.write(f"{headline.text}\n" )
        print(headline.text)
    print("\nSuccessfully scraped TradingView 🍾🍾🍾")
else:
    print("No headlines found.")

print("")
time.sleep(2)
driver.quit()

# Remove empty lines and duplicates from news.txt
with open("news.txt", "r") as infile:
    lines = infile.readlines()

seen = set()
cleaned_lines = []
for line in lines:
    stripped = line.strip()
    if stripped and stripped not in seen:
        cleaned_lines.append(line)
        seen.add(stripped)

with open("news.txt", "w") as outfile:
    outfile.writelines(cleaned_lines)

os.startfile("news.txt")

