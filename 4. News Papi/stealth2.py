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

# Import our human behavior module
from human_behavior import (
    human_like_delay, 
    human_like_typing, 
    simulate_human_browsing
)

def create_images_directory():
    """Create images directory if it doesn't exist"""
    if not os.path.exists("images"):
        os.makedirs("images")
        print("✓ Created 'images' directory")

def create_stealth_chrome_driver(headless=False):
    """PART 1: Create maximally stealthy Chrome driver with advanced anti-detection"""
    print("Creating stealth Chrome driver...")
    
    options = uc.ChromeOptions()
    
    # Basic stealth arguments
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    
    # Core anti-detection features
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # Advanced anti-detection arguments
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-features=AutomationControlled')
    options.add_argument('--exclude-switches=enable-automation')
    options.add_argument('--disable-ipc-flooding-protection')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    
    # Realistic user agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Additional preferences to avoid detection
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Create driver with stealth patches
        driver = uc.Chrome(options=options, use_subprocess=False, version_main=None)
        
        # Execute additional stealth scripts after driver creation
        stealth_js = """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            window.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' })
                })
            });
        """
        
        driver.execute_script(stealth_js)
        
        # Override user agent via CDP
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Add script to evaluate on new document
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": stealth_js
        })
        
        print("✓ Stealth Chrome driver created successfully")
        return driver
        
    except Exception as e:
        print(f"✗ Failed to create stealth driver: {str(e)}")
        return None

def check_for_detection(driver):
    """Monitor browser console for detection messages"""
    try:
        logs = driver.get_log('browser')
        detection_keywords = ['1337', 'undetected', 'chromedriver', 'automation', 'bot']
        
        detection_messages = []
        for log in logs:
            message = log['message'].lower()
            if any(keyword in message for keyword in detection_keywords):
                detection_messages.append(log['message'])
        
        if detection_messages:
            print("⚠ DETECTION FOUND:")
            for msg in detection_messages:
                print(f"  {msg}")
            return True
        return False
    except:
        return False

def find_prompt_input_stealth(driver):
    """Find prompt input with multiple fallback methods"""
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
            print(f"Trying selector: {selector}")
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((by, selector))
            )
            print(f"✓ Found input with: {selector}")
            return element
        except:
            continue
    
    return None

def find_generate_button_stealth(driver):
    """Find generate button with multiple fallback methods"""
    button_selectors = [
        "#buttons > button:nth-child(8)",
        "button[onclick*='generate']",
        "#buttons button",
        "button:contains('Generate')",
        ".generate-btn",
        "[data-action='generate']"
    ]
    
    for selector in button_selectors:
        try:
            print(f"Trying button selector: {selector}")
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            print(f"✓ Found button with: {selector}")
            return button
        except:
            continue
    
    return None

def download_image_safely(url, filepath):
    """Download image with error handling and retries"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            return True
            
        except Exception as e:
            print(f"Download attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
            
    return False

def generate_image_stealth(prompt, counter=0, headless=False):
    """Complete stealth image generation using imported human behavior"""
    driver = None
    try:
        print(f"\n--- Processing Image {counter} (Full Stealth Mode) ---")
        print(f"Prompt: {prompt[:50]}...")
        
        # PART 1: Create stealth driver
        driver = create_stealth_chrome_driver(headless=headless)
        if not driver:
            raise Exception("Failed to create stealth driver")
        
        # Navigate to site with human-like delay
        print("Navigating to site...")
        driver.get("https://perchance.org/beautiful-people")
        
        # PART 2: Human-like behavior after page load (imported function)
        human_like_delay(3, 5)  # Wait like a human would
        
        # Check for detection early
        if check_for_detection(driver):
            raise Exception("Bot detection triggered")
        
        # Handle alert with human timing
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"Alert found: {alert.text}")
            human_like_delay(1, 2)  # Human pause before accepting
            alert.accept()
            human_like_delay(0.5, 1)
        except:
            print("No alert found")
        
        # PART 2: Simulate human browsing (imported function)
        simulate_human_browsing(driver)
        
        # Check for detection after browsing
        if check_for_detection(driver):
            raise Exception("Bot detection triggered after browsing simulation")
        
        # Find input field with stealth
        print("Looking for prompt input...")
        input_field = find_prompt_input_stealth(driver)
        if not input_field:
            raise Exception("Could not find prompt input field")
        
        # PART 2: Human-like interaction with input field
        print("Clicking input field...")
        input_field.click()
        human_like_delay(0.5, 1)
        
        # Type with human-like timing (imported function)
        print("Entering prompt with human-like typing...")
        human_like_typing(input_field, prompt)
        
        # Find generate button
        print("Looking for generate button...")
        button = find_generate_button_stealth(driver)
        if not button:
            raise Exception("Could not find generate button")
        
        # PART 2: Human-like button click
        print("Clicking generate button...")
        human_like_delay(1, 2)  # Pause before clicking
        button.click()
        
        print("✓ Generate button clicked - waiting for image generation...")
        
        # Wait for image generation with longer timeout
        import random
        generation_wait = random.uniform(15, 25)  # Random wait time
        print(f"Waiting {generation_wait:.1f} seconds for generation...")
        time.sleep(generation_wait)
        
        # Look for result image
        image_selectors = [
            "#resultImgEl",
            "img[id='resultImgEl']",
            ".result-image img",
            "img[src*='blob:']",
            "img[src*='data:image']"
        ]
        
        image_element = None
        for selector in image_selectors:
            try:
                print(f"Looking for image with selector: {selector}")
                image_element = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"✓ Found image with: {selector}")
                break
            except:
                continue
        
        if not image_element:
            raise Exception("Could not find generated image")
        
        # Get image URL
        image_url = image_element.get_attribute("src")
        if not image_url or image_url == "":
            raise Exception("Image URL is empty")
        
        print(f"✓ Image URL obtained: {image_url[:50]}...")
        
        # Download image
        filepath = f"images/{counter}.png"
        if download_image_safely(image_url, filepath):
            print(f"✓ Image {counter} saved successfully to {filepath}")
            
            # PART 2: Human-like behavior after success
            human_like_delay(2, 4)  # Pause like a human would
            
            return True
        else:
            raise Exception("Failed to download image")
            
    except Exception as e:
        print(f"✗ Error generating image {counter}: {str(e)}")
        return False
        
    finally:
        if driver:
            try:
                # PART 2: Human-like closing behavior
                human_like_delay(1, 2)
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
    """Main function with full stealth implementation"""
    print("=== AI Image Generator - Full Stealth Mode ===")
    print("Part 1: Advanced anti-detection + Part 2: Human-like behavior (imported)")
    
    # Create images directory
    create_images_directory()
    
    # Read prompts
    print("\n--- Loading Prompts ---")
    prompts = read_prompts_from_csv("prompts.csv")
    
    if not prompts:
        print("✗ No prompts to process")
        sys.exit(1)
    
    # Configuration
    print(f"\n--- Configuration ---")
    headless_mode = input("Run in headless mode? (not recommended for stealth) (y/n): ").lower().startswith('y')
    
    if headless_mode:
        print("⚠ Warning: Headless mode makes detection more likely")
    
    # Process images with full stealth
    print(f"\n--- Generating {len(prompts)} Images (Stealth Mode) ---")
    successful = 0
    failed = 0
    
    for idx, prompt in enumerate(prompts):
        print(f"\n{'='*60}")
        print(f"PROCESSING IMAGE {idx + 1}/{len(prompts)}")
        print(f"{'='*60}")
        
        success = generate_image_stealth(prompt, idx, headless_mode)
        
        if success:
            successful += 1
            print(f"✅ Image {idx} completed successfully")
        else:
            failed += 1
            print(f"❌ Image {idx} failed")
            
        # Human-like delay between generations (imported function)
        if idx < len(prompts) - 1:  # Don't delay after the last image
            import random
            delay = random.uniform(10, 20)  # Random delay between 10-20 seconds
            print(f"\n💤 Waiting {delay:.1f} seconds before next generation (human-like behavior)...")
            time.sleep(delay)
    
    # Final report
    print(f"\n{'='*60}")
    print(f"🎯 GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Images saved in: ./images/")
    print(f"📊 Success rate: {(successful/(successful+failed)*100):.1f}%")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {type(e).__name__}: {str(e)}")
