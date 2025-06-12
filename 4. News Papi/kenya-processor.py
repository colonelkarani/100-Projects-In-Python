import requests
import json
import csv
import os
import hashlib
import pandas as pd
from dotenv import load_dotenv
from typing import List, Dict, Set, Optional
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class NewsProcessor:
    """
    A comprehensive news processing system that:
    1. Reads scraped news from CSV
    2. Checks for duplicates
    3. Rewrites headlines using AI
    4. Generates image prompts
    5. Stores processed data
    """
    
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model_name = "qwen/qwen3-235b-a22b:free"
        
        # File paths
        self.input_news_file = "kenyans_news.csv"  # From your scraper
        self.processed_headlines_file = "processed_headlines.csv"
        self.image_prompts_file = "image_prompts.csv"
        self.duplicate_tracking_file = "processed_tracking.csv"
        
        # Duplicate tracking
        self.processed_headlines: Set[str] = set()
        self.processed_urls: Set[str] = set()
        self.content_hashes: Set[str] = set()
        
        self._load_existing_processed_data()
    
    def _load_existing_processed_data(self) -> None:
        """Load previously processed data to avoid duplicates"""
        try:
            if os.path.exists(self.duplicate_tracking_file):
                tracking_df = pd.read_csv(self.duplicate_tracking_file)
                self.processed_headlines = set(tracking_df['original_headline'].tolist())
                self.processed_urls = set(tracking_df['url'].tolist())
                self.content_hashes = set(tracking_df['content_hash'].tolist())
                logger.info(f"Loaded {len(self.processed_headlines)} previously processed headlines")
            else:
                logger.info("No previous processing data found - starting fresh")
        except Exception as e:
            logger.warning(f"Error loading existing data: {e}")
    
    def _generate_content_hash(self, headline: str, description: str) -> str:
        """Generate hash for content to detect near-duplicates"""
        content = f"{headline.lower().strip()}{description.lower().strip()}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _is_duplicate(self, headline: str, description: str, url: str) -> bool:
        """Check if this news item has already been processed"""
        content_hash = self._generate_content_hash(headline, description)
        
        if url in self.processed_urls:
            logger.info(f"Duplicate URL found: {url}")
            return True
        
        if headline in self.processed_headlines:
            logger.info(f"Duplicate headline found: {headline[:50]}...")
            return True
        
        if content_hash in self.content_hashes:
            logger.info(f"Duplicate content found: {headline[:50]}...")
            return True
        
        return False
    
    def _make_api_request(self, prompt: str, system_message: str) -> Optional[str]:
        """Make API request to OpenRouter with error handling"""
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-site.com",
            "X-Title": "News Processor"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": system_message + prompt
                }
            ]
        }
        
        try:
            response = requests.post(
                url=self.base_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    return response_data['choices'][0]['message']['content'].strip()
                else:
                    logger.error("No choices in API response")
                    return None
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            return None
    
    def rewrite_headline(self, original_headline: str) -> Optional[str]:
        """Rewrite headline to make it more engaging"""
        system_message = (
            "Rewrite this headline to make it more engaging. "
            "Output only the headline as plain text, nothing else please! "
            "If you put anything else my program will crash and please no recommendations "
            "just the renovated headlines in plain text. This is the headline: "
        )
        
        rewritten = self._make_api_request(original_headline, system_message)
        if rewritten:
            logger.info(f"Headline rewritten: {original_headline[:30]}... -> {rewritten[:30]}...")
        return rewritten
    
    def generate_image_prompt(self, headline: str, description: str) -> Optional[str]:
        """Generate image description prompt for the news"""
        news_content = f"{headline}. {description}"
        system_message = (
            "Think like an expert. Describe an image that would visually represent this news. "
            "My AI model does not render text well so do not include image descriptions of text. "
            "This is also a Kenyan website so try to include a Kenyan context not so much but slightly. "
            "Make the users be able to connect with the image. "
            "Output only the description, nothing else please. "
            "Treat every prompt as separate and please don't output anything else other than the prompt in plain text: "
        )
        
        image_prompt = self._make_api_request(news_content, system_message)
        if image_prompt:
            logger.info(f"Image prompt generated for: {headline[:30]}...")
        return image_prompt
    
    def _save_processed_headline(self, original_headline: str, rewritten_headline: str, 
                                description: str, url: str) -> None:
        """Save processed headline to CSV"""
        try:
            file_exists = os.path.exists(self.processed_headlines_file)
            with open(self.processed_headlines_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['original_headline', 'rewritten_headline', 'description', 'url'])
                writer.writerow([original_headline, rewritten_headline, description, url])
        except Exception as e:
            logger.error(f"Error saving processed headline: {e}")
    
    def _save_image_prompt(self, headline: str, image_prompt: str, url: str) -> None:
        """Save image prompt to CSV"""
        try:
            file_exists = os.path.exists(self.image_prompts_file)
            with open(self.image_prompts_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['headline', 'image_prompt', 'url'])
                writer.writerow([headline, image_prompt, url])
        except Exception as e:
            logger.error(f"Error saving image prompt: {e}")
    
    def _save_tracking_data(self, headline: str, description: str, url: str) -> None:
        """Save tracking data to prevent duplicates"""
        try:
            content_hash = self._generate_content_hash(headline, description)
            file_exists = os.path.exists(self.duplicate_tracking_file)
            
            with open(self.duplicate_tracking_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['original_headline', 'url', 'content_hash', 'processed_date'])
                writer.writerow([headline, url, content_hash, pd.Timestamp.now().isoformat()])
            
            # Update in-memory tracking
            self.processed_headlines.add(headline)
            self.processed_urls.add(url)
            self.content_hashes.add(content_hash)
            
        except Exception as e:
            logger.error(f"Error saving tracking data: {e}")
    
    def load_news_data(self) -> List[Dict[str, str]]:
        """Load news data from CSV file"""
        news_items = []
        
        try:
            if not os.path.exists(self.input_news_file):
                logger.error(f"Input file {self.input_news_file} not found!")
                return news_items
            
            with open(self.input_news_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'headline' in row and 'description' in row and 'url' in row:
                        news_items.append({
                            'headline': row['headline'].strip(),
                            'description': row['description'].strip(),
                            'url': row['url'].strip()
                        })
            
            logger.info(f"Loaded {len(news_items)} news items from {self.input_news_file}")
            return news_items
            
        except Exception as e:
            logger.error(f"Error loading news data: {e}")
            return news_items
    
    def process_all_news(self, delay_between_requests: float = 1.0) -> None:
        """Process all news items - rewrite headlines and generate image prompts"""
        news_items = self.load_news_data()
        
        if not news_items:
            logger.error("No news items to process!")
            return
        
        new_items_count = 0
        processed_count = 0
        
        logger.info(f"Starting to process {len(news_items)} news items...")
        
        for index, item in enumerate(news_items, 1):
            headline = item['headline']
            description = item['description']
            url = item['url']
            
            logger.info(f"Processing item {index}/{len(news_items)}: {headline[:50]}...")
            
            # Check for duplicates
            if self._is_duplicate(headline, description, url):
                logger.info(f"Skipping duplicate item: {headline[:50]}...")
                continue
            
            new_items_count += 1
            
            try:
                # Rewrite headline
                rewritten_headline = self.rewrite_headline(headline)
                if not rewritten_headline:
                    logger.warning(f"Failed to rewrite headline: {headline[:50]}...")
                    rewritten_headline = headline  # Use original if rewrite fails
                
                # Add delay to respect API limits
                time.sleep(delay_between_requests)
                
                # Generate image prompt
                image_prompt = self.generate_image_prompt(headline, description)
                if not image_prompt:
                    logger.warning(f"Failed to generate image prompt for: {headline[:50]}...")
                    image_prompt = f"A visual representation of: {headline}"
                
                # Save processed data
                self._save_processed_headline(headline, rewritten_headline, description, url)
                self._save_image_prompt(rewritten_headline, image_prompt, url)
                self._save_tracking_data(headline, description, url)
                
                processed_count += 1
                logger.info(f"✓ Successfully processed item {index}")
                
                # Add delay between requests
                time.sleep(delay_between_requests)
                
            except Exception as e:
                logger.error(f"Error processing item {index}: {e}")
                continue
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"NEWS PROCESSING COMPLETED")
        print(f"{'='*60}")
        print(f"Total items found: {len(news_items)}")
        print(f"New items processed: {new_items_count}")
        print(f"Successfully processed: {processed_count}")
        print(f"Duplicates skipped: {len(news_items) - new_items_count}")
        print(f"{'='*60}")
        print(f"Output files:")
        print(f"- Processed headlines: {self.processed_headlines_file}")
        print(f"- Image prompts: {self.image_prompts_file}")
        print(f"- Tracking data: {self.duplicate_tracking_file}")
        print(f"{'='*60}")

def main():
    """Main function to run the news processor"""
    print("Starting News Processing System...")
    print("-" * 50)
    
    # Initialize processor
    processor = NewsProcessor()
    
    # Check if API key is available
    if not processor.api_key:
        logger.error("API_KEY not found in environment variables!")
        print("Please set your API_KEY in the .env file")
        return
    
    # Process all news
    processor.process_all_news(delay_between_requests=1.5)  # 1.5 second delay between API calls

if __name__ == "__main__":
    main()
