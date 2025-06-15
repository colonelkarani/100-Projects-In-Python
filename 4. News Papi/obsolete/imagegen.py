import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import multiprocessing
import time
import requests
import csv
import os
import sys

def create_images_directory():
    """Create images directory if it doesn't exist"""
    if not os.path.exists("images"):
        os.makedirs("images")
        print("✓ Created 'images' directory")

def test_undetected_chrome():
    """Test if undetected_chromedriver works"""
    try:
        print("Testing undetected_chromedriver...")
        options = uc.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = uc.Chrome(options=options, use_subprocess=False)
        driver.get("https://www.google.com")
        time.sleep(2)
        driver.quit()
        print("✓ Undetected ChromeDriver working")
        return True
        
    except Exception as e:
        print(f"✗ Undetected ChromeDriver failed: {str(e)}")
        return False

def test_regular_selenium():
    """Test if regular Selenium works as fallback"""
    try:
        print("Testing regular Selenium ChromeDriver...")
        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.google.com")
        time.sleep(2)
        driver.quit()
        print("✓ Regular Selenium ChromeDriver working")
        return True
        
    except Exception as e:
        print(f"✗ Regular Selenium failed: {str(e)}")
        return False

def create_chrome_driver(use_undetected=True, headless=False):
    """Create Chrome driver with fallback options"""
    if use_undetected:
        try:
            options = uc.ChromeOptions()
            if headless:
                options.add_argument('--headless=new')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            return uc.Chrome(options=options, use_subprocess=False)
            
        except Exception as e:
            print(f"Undetected ChromeDriver failed: {str(e)}")
            print("Falling back to regular Selenium...")
            
    # Fallback to regular Selenium
    options = Options()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def debug_page_elements(driver):
    """Debug function to see what's actually on the page"""
    try:
        print("\n=== PAGE DEBUG INFO ===")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Look for any textarea elements
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        print(f"Found {len(textareas)} textarea elements:")
        for i, textarea in enumerate(textareas):
            print(f"  Textarea {i}: id='{textarea.get_attribute('id')}', class='{textarea.get_attribute('class')}'")
        
        # Look for any input elements
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(inputs)} input elements:")
        for i, input_elem in enumerate(inputs[:5]):  # Show first 5 only
            print(f"  Input {i}: id='{input_elem.get_attribute('id')}', type='{input_elem.get_attribute('type')}'")
            
        # Check page source for the element
        if "promptControllerTextarea" in driver.page_source:
            print("✓ promptControllerTextarea found in page source")
        else:
            print("✗ promptControllerTextarea NOT found in page source")
            
        # Look for common prompt-related elements
        prompt_related = driver.find_elements(By.CSS_SELECTOR, "*[id*='prompt'], *[class*='prompt']")
        print(f"Found {len(prompt_related)} prompt-related elements:")
        for elem in prompt_related[:3]:
            print(f"  Element: tag={elem.tag_name}, id='{elem.get_attribute('id')}', class='{elem.get_attribute('class')}'")
        
        print("=== END DEBUG INFO ===\n")
            
    except Exception as e:
        print(f"Debug error: {str(e)}")

def wait_for_page_ready(driver, timeout=30):
    """Wait for page to be fully interactive"""
    try:
        # Wait for document ready
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Additional wait for JavaScript to finish
        time.sleep(3)
        print("✓ Page is ready")
        return True
    except Exception as e:
        print(f"Page not ready: {str(e)}")
        return False

def find_prompt_input(driver, debug=False):
    """Try multiple methods to find the prompt input field"""
    if debug:
        debug_page_elements(driver)
    
    selectors_to_try = [
        (By.ID, "promptControllerTextarea"),
        (By.CSS_SELECTOR, "#promptControllerTextarea"),
        (By.CSS_SELECTOR, "textarea[id='promptControllerTextarea']"),
        (By.XPATH, "//textarea[@id='promptControllerTextarea']"),
        (By.XPATH, "//textarea[contains(@id, 'prompt')]"),
        (By.CSS_SELECTOR, "textarea"),  # Any textarea as last resort
    ]
    
    for by, selector in selectors_to_try:
        try:
            print(f"Trying selector: {by} = '{selector}'")
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((by, selector))
            )
            print(f"✓ SUCCESS with: {by} = '{selector}'")
            return element
        except:
            print(f"✗ Failed: {by} = '{selector}'")
            continue
    
    return None

def download_image_safely(url, filepath):
    """Download image with error handling and retries"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            return True
            
        except Exception as e:
            print(f"Download attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
            
    return False

def generate_image(prompt, counter=0, use_undetected=True, headless=False, debug=False):
    """Generate image with comprehensive error handling"""
    driver = None
    try:
        print(f"\n--- Processing Image {counter} ---")
        print(f"Prompt: {prompt[:50]}...")
        
        # Create driver
        driver = create_chrome_driver(use_undetected, headless)
        print(f"✓ Chrome driver initialized for image {counter}")
        
        # Navigate to site
        driver.get("https://perchance.org/beautiful-people")
        print(f"✓ Page loaded for image {counter}")
        
        # Handle alert if present
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"Alert detected: {alert.text}")
            alert.accept()
        except:
            pass  # No alert present
        
        # Wait for page to be ready
        if not wait_for_page_ready(driver):
            raise Exception("Page did not load properly")
        
        # Find prompt input field
        input_field = find_prompt_input(driver, debug)
        if not input_field:
            raise Exception("Could not find prompt input field with any method")
            
        # Enter prompt
        input_field.click()
        input_field.clear()
        input_field.send_keys(prompt)
        print(f"✓ Prompt entered for image {counter}")
        
        # Find generate button - try multiple selectors
        button_selectors = [
            "#buttons > button:nth-child(8)",
            "button[onclick*='generate']",
            "button:contains('Generate')",
            "#buttons button",
        ]
        
        button = None
        for selector in button_selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                print(f"✓ Found button with selector: {selector}")
                break
            except:
                continue
                
        if not button:
            raise Exception("Could not find generate button")
            
        button.click()
        print(f"✓ Generate button clicked for image {counter}")
        
        # Wait for image generation
        print("Waiting for image generation...")
        time.sleep(15)
        
        # Find result image
        image_selectors = [
            "#resultImgEl",
            "img[id='resultImgEl']",
            ".result-image img",
            "img[src*='blob:']",
        ]
        
        image_element = None
        for selector in image_selectors:
            try:
                image_element = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"✓ Found image with selector: {selector}")
                break
            except:
                continue
                
        if not image_element:
            raise Exception("Could not find generated image")
            
        # Get image source
        image_url = image_element.get_attribute("src")
        if not image_url or image_url == "":
            raise Exception("Image URL is empty")
            
        print(f"✓ Image URL obtained for image {counter}")
        
        # Download image
        filepath = f"images/{counter}.png"
        if download_image_safely(image_url, filepath):
            print(f"✓ Image {counter} saved successfully to {filepath}")
            return True
        else:
            raise Exception("Failed to download image")
            
    except Exception as e:
        print(f"✗ Error generating image {counter}: {type(e).__name__}: {str(e)}")
        if debug and driver:
            input("Press Enter to close browser and continue...")
        return False
        
    finally:
        if driver:
            try:
                driver.quit()
                print(f"✓ Driver closed for image {counter}")
            except:
                print(f"⚠ Warning: Error closing driver for image {counter}")

def read_prompts_from_csv(filename):
    """Read prompts from CSV file with error handling"""
    prompts = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                if row and row[0].strip():  # Skip empty rows
                    prompts.append(row[0].strip())
                    
        print(f"✓ Loaded {len(prompts)} prompts from {filename}")
        return prompts
        
    except FileNotFoundError:
        print(f"✗ Error: Could not find {filename}")
        print("Creating sample prompts.csv file...")
        
        # Create sample CSV
        sample_prompts = [
            "a beautiful portrait of a person",
            "a landscape with mountains and trees",
            "a futuristic city skyline at sunset",
            "a cat sitting in a garden",
            "an abstract painting with vibrant colors"
        ]
        
        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for prompt in sample_prompts:
                writer.writerow([prompt])
                
        print(f"✓ Created sample {filename} with {len(sample_prompts)} prompts")
        return sample_prompts
        
    except Exception as e:
        print(f"✗ Error reading {filename}: {str(e)}")
        return []

def main():
    """Main function to orchestrate the image generation process"""
    print("=== AI Image Generator ===")
    print("Learning Python: modules, exception handling, functions, multiprocessing")
    
    # Create images directory
    create_images_directory()
    
    # Test Chrome setup
    print("\n--- Testing Chrome Setup ---")
    undetected_works = test_undetected_chrome()
    regular_works = test_regular_selenium()
    
    if not undetected_works and not regular_works:
        print("✗ Both Chrome drivers failed. Please check your Chrome installation.")
        sys.exit(1)
        
    # Determine which driver to use
    use_undetected = undetected_works
    print(f"✓ Will use {'undetected' if use_undetected else 'regular'} ChromeDriver")
    
    # Read prompts
    print("\n--- Loading Prompts ---")
    prompts = read_prompts_from_csv("prompts.csv")
    
    if not prompts:
        print("✗ No prompts to process")
        sys.exit(1)
    
    # Ask user for preferences
    print(f"\n--- Configuration ---")
    debug_mode = input("Enable debug mode? (y/n): ").lower().startswith('y')
    headless_mode = input("Run in headless mode? (y/n): ").lower().startswith('y')
    
    if debug_mode:
        print("Debug mode enabled - browser will stay visible longer")
        headless_mode = False  # Force non-headless for debugging
    
    # Process images
    print(f"\n--- Generating {len(prompts)} Images ---")
    successful = 0
    failed = 0
    
    for idx, prompt in enumerate(prompts):
        success = generate_image(prompt, idx, use_undetected, headless_mode, debug_mode)
        
        if success:
            successful += 1
        else:
            failed += 1
            
        # Delay between generations to prevent overload
        if idx < len(prompts) - 1:  # Don't delay after the last image
            delay = 10 if debug_mode else 5
            print(f"Waiting {delay} seconds before next generation...")
            time.sleep(delay)
    
    # Final report
    print(f"\n=== Generation Complete ===")
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    print(f"📁 Images saved in: ./images/")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {type(e).__name__}: {str(e)}")
