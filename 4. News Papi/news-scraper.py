#block-kenyans-content > div > div > div.view-content > div > ul > li:nth-child(1) > div > h2 > a

from selenium import webdriver
from selenium.webdriver.common.by import By
# Initialize the WebDriver (make sure to specify the path to your WebDriver)
driver = webdriver.Chrome()  # or webdriver.Firefox(), etc.
# Open the desired webpage
driver.get('https://www.kenyans.co.ke/news')
# Select the element by ID
#block-kenyans-content > div > div > div.view-content > div > ul > li:nth-child(1) > div > h2 > a

link = driver.find_element(By.XPATH, '//*[@id="block-kenyans-content"]/div/div/div[1]/div/ul/li[1]/div/h2/a')

print(link.text)
# Close the driver when done
driver.quit()