from selenium import webdriver
import time

driver = webdriver.Chrome()

try:
    driver.get("https://www.ecomed.com.au/wp-content/uploads/2015/11/specula_cusco.jpg")
    driver.fullscreen_window()
    
    time.sleep(20)

finally:
    driver.quit()