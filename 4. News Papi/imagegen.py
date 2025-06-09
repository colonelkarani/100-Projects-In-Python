from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options   
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import requests
import time 
import os 
from dotenv import load_dotenv

load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

options = Options()
options.add_argument("--headless")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument('--disable-web-security')

driver = webdriver.Chrome(options=options)

def generate(prompt, counter=0):
    try:
        driver.get("https://deepai.org/machine-learning-model/text2img")
        wait = WebDriverWait(driver, 15)

        buttonz = wait.until(EC.element_to_be_clickable(
            (By.ID, "headerLoginButton")
        ))
        buttonz.click()

        buttonza = wait.until(EC.element_to_be_clickable(
            (By.ID, "switch-to-email")
        ))
        buttonza.click()
        
        input_email = wait.until(EC.presence_of_element_located(
            (By.ID, "user-email")
        ))
        input_email.clear()
        input_email.send_keys(email)
        time.sleep(5)
        input_password = wait.until(EC.presence_of_element_located(
            (By.NAME, "password")
        ))
        input_password.clear()
        input_password.send_keys(password)

        button0 = wait.until(EC.element_to_be_clickable(
            (By.ID, "login-via-email-id")
        ))
        button0.click()
        time.sleep(10)
       # wait.until(EC.url_contains("/profile")) 
        # Fix 1: Use element singular locator
        input_field = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "textarea.model-input-text-input")
        ))
        
        # Clear existing text and send prompt
        input_field.clear()
        input_field.send_keys(prompt)
        
        # Fix 2: Use element singular locator for button
        button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button#modelSubmitButton")
        ))
        button.click()
        time.sleep(10)
        try:
            ad_frame = driver.find_element(By.CSS_SELECTOR, "iframe#google_ads_iframe_")
            driver.switch_to.frame(ad_frame)
            driver.find_element(By.CSS_SELECTOR, "div.close-button").click()
        except:
            pass
        driver.switch_to.default_content()
        
        # Wait for image generation and get source
        image = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#place_holder_picture_model > img")
        ))
        image_link = image.get_attribute("src")
        
        # Save image with unique name
        with open(f"images/{counter}.png", "wb") as f:
            img_data = requests.get(image_link).content
            f.write(img_data)
            
        time.sleep(10)  # Add delay between generations
            
    except Exception as e:
        print(f"Error generating image {counter}: {str(e)}")

# Fix 3: Proper CSV handling
with open("prompts.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for idx, row in enumerate(reader):
        if row:  # Skip empty rows
            generate(row[0], idx)  # Use first column value as prompt

driver.quit()
