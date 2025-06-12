from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time
import csv
import logging

# Setup logging for better error tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_driver():
    """Setup Chrome driver with appropriate options"""
    chrome_options = Options()
 
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    try:
        service = Service()  # Uses default ChromeDriver path
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Chrome driver initialized successfully")
        return driver
    except WebDriverException as e:
        logger.error(f"Error initializing WebDriver: {e}")
        return None

def scrape_kenyans_news():
    """Main function to scrape news headlines and descriptions"""
    driver = setup_driver()
    if not driver:
        logger.error("Failed to initialize driver. Exiting.")
        return
    
    try:
        # Navigate to the news page
        url = 'https://www.kenyans.co.ke/news'
        logger.info(f"Navigating to {url}")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "block-kenyans-content")))
        
        data = []
        
        # Find all headline links using the CSS selector
        headline_selector = '#block-kenyans-content div.view-content div ul li div h2 a'
        
        try:
            # Wait for headlines to load
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, headline_selector)))
            headline_links = driver.find_elements(By.CSS_SELECTOR, headline_selector)
            logger.info(f"Found {len(headline_links)} headlines")
            
            # Store headline data first to avoid stale element references
            headlines_data = []
            for link in headline_links:
                try:
                    headline_text = link.text.strip()
                    headline_url = link.get_attribute('href')
                    if headline_text and headline_url:
                        headlines_data.append({
                            'headline': headline_text,
                            'url': headline_url
                        })
                except Exception as e:
                    logger.warning(f"Error extracting headline data: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(headlines_data)} headline URLs")
            
            # Now visit each article to get descriptions
            for index, headline_data in enumerate(headlines_data, 1):
                try:
                    logger.info(f"Processing article {index}/{len(headlines_data)}: {headline_data['headline'][:50]}...")
                    
                    # Navigate to the article
                    driver.get(headline_data['url'])
                    
                    # Wait for article content to load
                    wait.until(EC.presence_of_element_located((By.ID, "block-kenyans-content")))
                    time.sleep(2)  # Additional wait for content to fully render
                    
                    # Try multiple XPath selectors for description
                    description_selectors = [
                        '//*[@id="block-kenyans-content"]/article/div/div[4]/div/div[2]/div',  # Your provided XPath
                        '//*[@id="block-kenyans-content"]/article/div/div/div/div/div',      # Alternative
                        '//article//div[contains(@class, "field-type-text-with-summary")]', # Generic content
                        '//article//div[contains(@class, "content")]',                      # Another generic
                        '//article//p'  # Fallback to paragraphs
                    ]
                    
                    description = "Description not found"
                    for selector in description_selectors:
                        try:
                            if selector.startswith('//'):
                                description_element = driver.find_element(By.XPATH, selector)
                            else:
                                description_element = driver.find_element(By.XPATH, selector)
                            
                            description = description_element.text.strip()
                            if description and len(description) > 20:  # Ensure we got meaningful content
                                break
                        except NoSuchElementException:
                            continue
                    
                    # Store the complete data
                    article_data = {
                        'headline': headline_data['headline'],
                        'description': description,
                        'url': headline_data['url']
                    }
                    data.append(article_data)
                    
                    logger.info(f"✓ Article {index} processed successfully")
                    
                    # Small delay to be respectful to the server
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing article {index}: {e}")
                    # Still add the headline even if description fails
                    data.append({
                        'headline': headline_data['headline'],
                        'description': f"Error retrieving description: {str(e)}",
                        'url': headline_data['url']
                    })
                    continue
        
        except TimeoutException:
            logger.error("Timeout waiting for headlines to load")
            return
        except Exception as e:
            logger.error(f"Error finding headlines: {e}")
            return
        
        # Save data to CSV
        if data:
            save_to_csv(data)
        else:
            logger.warning("No data collected to save")
            
    except Exception as e:
        logger.error(f"Unexpected error during scraping: {e}")
    finally:
        # Always close the driver
        driver.quit()
        logger.info("Driver closed successfully")

def save_to_csv(data):
    """Save scraped data to CSV file"""
    csv_filename = 'kenyans_news.csv'
    
    try:
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['headline', 'description', 'url']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data
            for row in data:
                writer.writerow(row)
        
        logger.info(f"✓ Successfully saved {len(data)} articles to {csv_filename}")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"SCRAPING COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"Total articles scraped: {len(data)}")
        print(f"Data saved to: {csv_filename}")
        print(f"{'='*60}")
        
        # Print first few headlines as preview
        print("\nPreview of scraped headlines:")
        for i, item in enumerate(data[:3], 1):
            print(f"{i}. {item['headline']}")
            print(f"   Description: {item['description'][:100]}...")
            print(f"   URL: {item['url']}")
            print()
            
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    print("Starting Kenyans.co.ke News Scraper...")
    print("Make sure you have Chrome and ChromeDriver installed!")
    print("-" * 50)
    
    scrape_kenyans_news()
