from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
print( '''
      
            o8o                       .o8                  .o8        .o8              
            `"'                      "888                 "888       "888              
oo.ooooo.  oooo   .ooooo.        .oooo888   .oooo.    .oooo888   .oooo888  oooo    ooo 
 888' `88b `888  d88' `"Y8      d88' `888  `P  )88b  d88' `888  d88' `888   `88.  .8'  
 888   888  888  888            888   888   .oP"888  888   888  888   888    `88..8'   
 888   888  888  888   .o8      888   888  d8(  888  888   888  888   888     `888'    
 888bod8P' o888o `Y8bod8P'      `Y8bod88P" `Y888""8o `Y8bod88P" `Y8bod88P"     .8'     
 888                                                                       .o..P'      
o888o                                                                      `Y8P'       
                                                                                       

      ''')
time.sleep(1)

model = int(input('''
What model do you want to use today? (pick a number only please)
    1. Craiyon
    2. Deepai(personally i prefer this)
'''))


user_prompt = input("What image do  you want to create today. Let you imagination run wild:  ")
image_name= input("What do you want to name your picture (dont put spaces please): ")


def craiyon():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get('https://www.craiyon.com/')
    prompt = driver.find_element(By.ID, "prompt")
    button = driver.find_element(By.XPATH, "//button[.//p[text()='Draw now']]")

    prompt.send_keys(user_prompt)
    button.click()

    images = driver.find_element(By.CSS_SELECTOR, "#pro-images-card > div.w-full.grid.grid-cols-4.gap-2 >   div > div > div:nth-child(1) > a > img")
    image_link = images.get_attribute("src")
    respo = requests.get(image_link)
    with open(image_name+".png", "wb") as f :
        f.write(respo.content)

def deepai():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get('https://www.craiyon.com/')
    prompt = driver.find_element(By.ID, "prompt")
    button = driver.find_element(By.XPATH, "//button[.//p[text()='Draw now']]")

    prompt.send_keys(user_prompt)
    button.click()

    images = driver.find_element(By.CSS_SELECTOR, "#pro-images-card > div.w-full.grid.grid-cols-4.gap-2 >   div > div > div:nth-child(1) > a > img")
    image_link = images.get_attribute("src")
    respo = requests.get(image_link)
    with open(image_name+".png", "wb") as f :
        f.write(respo.content)

if model == 1:
    craiyon()
elif model ==2:
    deepai()



driver.quit()