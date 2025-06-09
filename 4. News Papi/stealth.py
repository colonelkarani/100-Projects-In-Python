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
import random
import platform

# Import our human behavior module
try:
    from human_behavior import (
        human_like_delay, 
        human_like_typing, 
        simulate_human_browsing
    )
    HUMAN_BEHAVIOR_AVAILABLE = True
except ImportError:
    print("⚠ Warning: human_behavior.py not found. Running without human behavior simulation.")
    HUMAN_BEHAVIOR_AVAILABLE = False
    
    # Define fallback functions
    def human_like_delay(min_seconds=1, max_seconds=3):
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def human_like_typing(element, text):
        element.clear()
        element.send_keys(text)
    
    def simulate_human_browsing(driver):
        time.sleep(2)

def create_images_directory():
    """Create images directory if it doesn't exist"""
    if not os.path.exists("images"):
        os.makedirs("images")
        print("✓ Created 'images' directory")

def find_chrome_executable():
    """Find Chrome executable path"""
    system = platform.system()
    
    if system == "Windows":
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
    else:  # Linux
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium"
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ Found Chrome at: {path}")
            return path
    
    print("✗ Chrome executable not found in standard locations")
    return None

def create_stealth_chrome_driver(headless=False):
    """PART 1: Create maximally stealthy Chrome driver with detailed error logging"""
    print("Creating stealth Chrome driver...")
    
    try:
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
        
        # Add Chrome path if needed
        chrome_path = find_chrome_executable()
        if chrome_path:
            options.binary_location = chrome_path
        
        # Additional preferences
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        print("✓ Chrome options configured")
        
        # Try to create driver with detailed error catching
        print("Attempting to create undetected Chrome driver...")
        driver = uc.Chrome(options=options, use_subprocess=False, version_main=None)
        print("✓ Undetected Chrome driver created")
        
        # Execute stealth scripts
        print("Applying stealth JavaScript patches...")
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
        print("✓ Stealth JavaScript applied")
        
        # Override user agent via CDP
        try:
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Add script to evaluate on new document
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                "source": stealth_js
            })
            print("✓ CDP commands executed")
        except Exception as cdp_error:
            print(f"⚠ Warning: CDP commands failed: {str(cdp_error)} (continuing anyway)")
        
        # Test basic functionality
        print("Testing driver functionality...")
        driver.get("data:text/html,<html><body><h1>Driver Test Success</h1></body></html>")
        print("✓ Driver test successful")
        
        print("✓ Stealth Chrome driver created successfully")
        return driver
        
    except Exception as e:
        print(f"✗ Detailed error in create_stealth_chrome_driver: {type(e).__name__}: {str(e)}")
        print(f"Error details: {repr(e)}")
        return None

def create_minimal_driver(headless=False):
    """Create minimal Chrome driver with basic options only"""
    try:
        print("Creating minimal undetected Chrome driver...")
        options = uc.ChromeOptions()
        
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Add Chrome path if needed
        chrome_path = find_chrome_executable()
        if chrome_path:
            options.binary_location = chrome_path
        
        driver = uc.Chrome(options=options, use_subprocess=False)
        print("✓ Minimal undetected driver created successfully")
        return driver
        
    except Exception as e:
        print(f"✗ Minimal undetected driver failed: {str(e)}")
        return None

def create_regular_selenium_driver(headless=False):
    """Create regular Selenium Chrome driver as final fallback"""
    try:
        print("Creating regular Selenium Chrome driver...")
        options = Options()
        
        if headless:
            options.add_argument('--headless=new')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Add Chrome path if needed
        chrome_path = find_chrome_executable()
        if chrome_path:
            options.binary_location = chrome_path
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("✓ Regular Selenium driver created successfully")
        return driver
        
    except Exception as e:
        print(f"✗ Regular Selenium driver failed: {str(e)}")
        return None

def test_driver_creation():
    """Test different driver creation methods"""
    print("\n=== Testing Driver Creation Methods ===")
    
    # Test 1: Basic undetected_chromedriver
    try:
        print("Test 1: Basic undetected_chromedriver...")
        driver = uc.Chrome(use_subprocess=False)
        print("✓ Basic undetected_chromedriver works")
        driver.quit()
    except Exception as e:
        print(f"✗ Basic undetected_chromedriver failed: {str(e)}")
    
    # Test 2: Regular Selenium
    try:
        print("Test 2: Regular Selenium...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        print("✓ Regular Selenium works")
        driver.quit()
    except Exception as e:
        print(f"✗ Regular Selenium failed: {str(e)}")
    
    # Test 3: Chrome executable detection
    chrome_path = find_chrome_executable()
    if chrome_path:
        print(f"✓ Chrome executable found: {chrome_path}")
    else:
        print("✗ Chrome executable not found in standard locations")
    
    print("=== Driver Creation Test Complete ===\n")

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
    except Exception as e:
        print(f"⚠ Warning: Could not check console logs: {str(e)}")
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
    
    print("✗ Could not find prompt input with any selector")
    return None

def find_generate_button_stealth(driver):
    """Find generate button with multiple fallback methods"""
    button_selectors = [
        "#buttons > button:nth-child(8)",
        "button[onclick*='generate']",
        "#buttons button",
        "button:contains('Generate')",
        ".generate-btn",
        "[data-action='generate']",
        "button[type='submit']",
        ".btn-primary",
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
    
    print("✗ Could not find generate button with any selector")
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
    """Generate image with multiple driver fallback strategies"""
    driver = None
    try:
        print(f"\n--- Processing Image {counter} (Full Stealth Mode) ---")
        print(f"Prompt: {prompt[:50]}...")
        
        # Try multiple driver creation strategies
        print("Strategy 1: Full stealth driver...")
        driver = create_stealth_chrome_driver(headless=headless)
        
        if not driver:
            print("Strategy 2: Minimal undetected driver...")
            driver = create_minimal_driver(headless=headless)
        
        if not driver:
            print("Strategy 3: Regular Selenium driver...")
            driver = create_regular_selenium_driver(headless=headless)
        
        if not driver:
            raise Exception("All driver creation strategies failed")
        
        print("✓ Driver created successfully, proceeding with generation...")
        
        # Navigate to site with human-like delay
        print("Navigating to site...")
        driver.get("https://perchance.org/beautiful-people")
        
        # Human-like behavior after page load (using imported or fallback function)
        human_like_delay(3, 5)  # Wait like a human would
        
        # Check for detection early
        if check_for_detection(driver):
            print("⚠ Bot detection triggered, but continuing...")
        
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
        
        # Simulate human browsing (using imported or fallback function)
        simulate_human_browsing(driver)
        
        # Check for detection after browsing
        if check_for_detection(driver):
            print("⚠ Bot detection triggered after browsing, but continuing...")
        
        # Find input field with stealth
        print("Looking for prompt input...")
        input_field = find_prompt_input_stealth(driver)
        if not input_field:
            raise Exception("Could not find prompt input field")
        
        # Human-like interaction with input field
        print("Clicking input field...")
        input_field.click()
        human_like_delay(0.5, 1)
        
        # Type with human-like timing (using imported or fallback function)
        print("Entering prompt with human-like typing...")
        human_like_typing(input_field, prompt)
        
        # Find generate button
        print("Looking for generate button...")
        button = find_generate_button_stealth(driver)
        if not button:
            raise Exception("Could not find generate button")
        
        # Human-like button click
        print("Clicking generate button...")
        human_like_delay(1, 2)  # Pause before clicking
        button.click()
        
        print("✓ Generate button clicked - waiting for image generation...")
        
        # Wait for image generation with longer timeout
        generation_wait = random.uniform(15, 25)  # Random wait time
        print(f"Waiting {generation_wait:.1f} seconds for generation...")
        time.sleep(generation_wait)
        
        # Look for result image
        image_selectors = [
            "#resultImgEl",
            "img[id='resultImgEl']",
            ".result-image img",
            "img[src*='blob:']",
            "img[src*='data:image']",
            "img[src*='perchance']",
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
            
            # Human-like behavior after success
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
                # Human-like closing behavior
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
    """Main function with full stealth implementation and robust error handling"""
    print("=== AI Image Generator - Full Stealth Mode ===")
    print("Part 1: Advanced anti-detection + Part 2: Human-like behavior")
    
    if HUMAN_BEHAVIOR_AVAILABLE:
        print("✓ Human behavior module loaded")
    else:
        print("⚠ Using fallback human behavior functions")
    
    # Test driver creation first
    test_driver_creation()
    
    # Create images directory
    create_images_directory()
    
    # Read prompts
    print("--- Loading Prompts ---")
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
            
        # Human-like delay between generations
        if idx < len(prompts) - 1:  # Don't delay after the last image
            delay = random.uniform(10, 20)  # Random delay between 10-20 seconds
            print(f"\n💤 Waiting {delay:.1f} seconds before next generation (human-like behavior)...")
            time.sleep(delay)
    
    # Final report
    print(f"\n{'='*60}")
    print(f"🎯 GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    if successful + failed > 0:
        print(f"📊 Success rate: {(successful/(successful+failed)*100):.1f}%")
    print(f"📁 Images saved in: ./images/")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
