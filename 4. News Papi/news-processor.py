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
import urllib.parse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class NewsProcessor:
    """
    A comprehensive news processing system that:
    1. Reads scraped news from CSV
    2. Checks for duplicates across all operations
    3. Rewrites headlines AND descriptions using AI
    4. Generates image prompts and creates actual images
    5. Stores all processed data in a master CSV file
    6. Handles API failures with multiple keys and retries
    """
    
    def __init__(self):
        # Multiple API configurations - same format, different keys and models
        self.api_configs = [
            {
                'name': 'Qwen',
                'api_key': os.getenv('API_KEY_1'),
                'base_url': "https://api-inference.huggingface.co/models/meta-llama/llama-4-maverick:free",
                'model': "DeepSeek-R1-0528-Qwen3-8B"
            },
            {
                'name': 'Deepseek Chimera',
                'api_key': os.getenv('API_KEY_2'),
                'base_url': "https://openrouter.ai/api/v1/chat/completions",
                'model': "deepseek/deepseek-r1-0528:free"
            },
            {
                'name': 'Sarvam',
                'api_key': os.getenv('API_KEY_3'),
                'base_url': "https://openrouter.ai/api/v1/chat/completions",
                'model': "sarvamai/sarvam-m:free"
            },
            {
                'name': 'Deepseek V3',
                'api_key': os.getenv('API_KEY_4'),
                'base_url': "https://openrouter.ai/api/v1/chat/completions",
                'model': "deepseek/deepseek-chat-v3-0324:free"
            },
            {
                'name': 'Intern V',
                'api_key': os.getenv('API_KEY_5'),
                'base_url': "https://openrouter.ai/api/v1/chat/completions",
                'model': "opengvlab/internvl3-14b:free"
            }
        ]
        
        # Filter out configs without API keys
        self.api_configs = [config for config in self.api_configs if config['api_key']]
        self.current_api_index = 0
        
        # File paths
        self.input_news_file = "kenyans_news.csv"
        self.master_output_file = "processed_news_master.csv"
        self.duplicate_tracking_file = "processed_tracking.csv"
        self.images_folder = "generated_images"
        
        # Duplicate tracking
        self.processed_headlines: Set[str] = set()
        self.processed_urls: Set[str] = set()
        self.content_hashes: Set[str] = set()
        
        # Create images folder
        os.makedirs(self.images_folder, exist_ok=True)
        
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
        try:
            if not headline or not description:
                logger.warning("Empty headline or description for hash generation")
                return "unknown_" + str(int(time.time()))
            
            content = f"{headline.lower().strip()}{description.lower().strip()}"
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Ensure hash is at least 8 characters (MD5 is always 32, but being defensive)
            if len(content_hash) < 8:
                logger.warning(f"Generated hash is unexpectedly short: {content_hash}")
                content_hash = (content_hash + "00000000")[:8]
            
            logger.debug(f"Generated content hash: '{content_hash}' for headline: '{headline[:50]}'")
            return content_hash
        except Exception as e:
            logger.error(f"Error generating content hash: {e}")
            return "error_" + str(int(time.time()))
    
    def _is_duplicate(self, headline: str, description: str, url: str) -> bool:
        """Check if this news item has already been processed"""
        try:
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
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            return False
    
    def _get_current_api_config(self) -> Optional[Dict]:
        """Get current API configuration"""
        if self.current_api_index < len(self.api_configs):
            return self.api_configs[self.current_api_index]
        return None
    
    def _switch_to_next_api_key(self) -> bool:
        """Switch to next API key, return False if no more keys available"""
        self.current_api_index += 1
        if self.current_api_index < len(self.api_configs):
            config = self._get_current_api_config()
            logger.info(f"Switching to {config['name']} (API {self.current_api_index + 1})")
            return True
        return False
    
    def _make_api_request(self, prompt: str, system_message: str, max_retries: int = 3) -> Optional[str]:
        """Make API request with error handling and API key fallback"""
        for attempt in range(max_retries):
            config = self._get_current_api_config()
            
            if not config:
                logger.error("No API configurations available!")
                return None
            
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://your-site.com",
                "X-Title": "News Processor"
            }
            
            payload = {
                "model": config['model'],
                "messages": [
                    {
                        "role": "user",
                        "content": system_message + prompt
                    }
                ]
            }
            
            try:
                response = requests.post(
                    url=config['base_url'],
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=30
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        message = response_data['choices'][0].get('message', {})
                        content = message.get('content', '')
                        if content:
                            return content.strip()
                        else:
                            logger.error("API response 'message' or 'content' missing or empty.")
                            return None
                    else:
                        logger.error("No choices in API response")
                        logger.debug(f"API response: {json.dumps(response_data)}")
                elif response.status_code == 401:
                    logger.error(f"API key authentication failed for {config['name']}")
                    if not self._switch_to_next_api_key():
                        logger.error("All API keys exhausted!")
                        return None
                    continue
                else:
                    logger.error(f"API Error for {config['name']}: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for {config['name']} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            except Exception as e:
                logger.error(f"Unexpected error in API request for {config['name']}: {e}")
                
        # If all retries failed, try next API key
        if self._switch_to_next_api_key():
            logger.info("Retrying with next API provider...")
            return self._make_api_request(prompt, system_message, max_retries)
        
        return None
    
    def rewrite_headline(self, original_headline: str) -> Optional[str]:
        """Rewrite headline to make it more engaging"""
        if not original_headline or not original_headline.strip():
            logger.warning("Empty headline provided for rewriting")
            return None
        
        system_message = (
            "Rewrite this headline to make it more engaging and clickable. "
            "Keep it concise but compelling. "
            "Output only the headline as plain text, nothing else please! "
            "If you put anything else my program will crash. "
            "Just the renovated headline in plain text. This is the headline: "
        )
        
        rewritten = self._make_api_request(original_headline, system_message)
        if rewritten:
            logger.info(f"Headline rewritten: {original_headline[:30]}... -> {rewritten[:30]}...")
        return rewritten
    
    def rewrite_description(self, original_description: str, headline: str) -> Optional[str]:
        """Rewrite description to make it more engaging"""
        if not original_description or not original_description.strip():
            logger.warning("Empty description provided for rewriting")
            return None
        
        system_message = (
            "Rewrite this news description to make it more engaging and informative. "
            "Keep the key facts but make it more compelling to read. "
            "Make it 2-3 sentences maximum. "
            "Output only the description as plain text, nothing else please! "
            "Context headline: " + (headline or "") + "\n"
            "Description to rewrite: "
        )
        
        rewritten = self._make_api_request(original_description, system_message)
        if rewritten:
            logger.info(f"Description rewritten for: {headline[:30]}...")
        return rewritten
    
    def generate_image_prompt(self, headline: str, description: str) -> Optional[str]:
        """Generate image description prompt for the news"""
        if not headline or not headline.strip():
            logger.warning("Empty headline provided for image prompt generation")
            return None
        
        news_content = f"{headline}. {description or ''}"
        system_message = (
            "Create a detailed image prompt for AI image generation based on this news. "
            "The image should visually represent the story. "
            "Do not include text in the image description. "
            "Include Kenyan context where appropriate. "
            "Make it engaging and relatable. "
            "Output only the image prompt, nothing else please: "
        )
        
        image_prompt = self._make_api_request(news_content, system_message)
        if image_prompt:
            logger.info(f"Image prompt generated for: {headline[:30]}...")
        return image_prompt
    
    def create_image(self, prompt: str, filename: str) -> Optional[str]:
        """Create image from prompt and save to file"""
        # Defensive checks
        if not prompt or not prompt.strip():
            logger.error("Image prompt is empty!")
            return None
        if not filename or not filename.strip():
            logger.error("Image filename is empty!")
            return None
        if not self.images_folder:
            logger.error("Images folder not set!")
            return None
        
        try:
            encoded_prompt = urllib.parse.quote(prompt.strip())
            url = "https://image.pollinations.ai/prompt/" + encoded_prompt
            
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                filepath = os.path.join(self.images_folder, f"{filename}.png")
                
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                logger.info(f"Image created: {filepath}")
                return filepath
            else:
                logger.error(f"Image generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating image: {e}")
            return None
    
    def _save_to_master_csv(self, data: Dict) -> None:
        """Save all processed data to master CSV file"""
        try:
            file_exists = os.path.exists(self.master_output_file)
            
            with open(self.master_output_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'original_headline', 'rewritten_headline',
                    'original_description', 'rewritten_description',
                    'image_prompt', 'image_filepath', 'url',
                    'content_hash', 'processed_date'
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(data)
                
        except Exception as e:
            logger.error(f"Error saving to master CSV: {e}")
    
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
                        headline = str(row['headline']).strip() if row['headline'] else ""
                        description = str(row['description']).strip() if row['description'] else ""
                        url = str(row['url']).strip() if row['url'] else ""
                        
                        if headline and description and url:
                            news_items.append({
                                'headline': headline,
                                'description': description,
                                'url': url
                            })
            
            logger.info(f"Loaded {len(news_items)} news items from {self.input_news_file}")
            return news_items
            
        except Exception as e:
            logger.error(f"Error loading news data: {e}")
            return news_items
    
    def process_all_news(self, delay_between_requests: float = 2.0) -> None:
        """Process all news items - rewrite headlines, descriptions, and create images"""
        news_items = self.load_news_data()
        
        if not news_items:
            logger.error("No news items to process!")
            return
        
        if not self.api_configs:
            logger.error("No API keys found! Please set API keys in your .env file")
            return
        
        new_items_count = 0
        processed_count = 0
        
        logger.info(f"Starting to process {len(news_items)} news items...")
        logger.info(f"Available API providers: {[config['name'] for config in self.api_configs]}")
        
        for index, item in enumerate(news_items, 1):
            headline = item.get('headline', '').strip()
            description = item.get('description', '').strip()
            url = item.get('url', '').strip()
            
            if not headline or not description or not url:
                logger.error(f"Skipping item {index} due to missing headline/description/url.")
                continue

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
                    rewritten_headline = headline
                
                time.sleep(delay_between_requests)
                
                # Rewrite description
                rewritten_description = self.rewrite_description(description, headline)
                if not rewritten_description:
                    logger.warning(f"Failed to rewrite description for: {headline[:50]}...")
                    rewritten_description = description
                
                time.sleep(delay_between_requests)
                
                # Generate image prompt
                image_prompt = self.generate_image_prompt(rewritten_headline, rewritten_description)
                if not image_prompt:
                    logger.warning(f"Failed to generate image prompt for: {headline[:50]}...")
                    image_prompt = f"A visual representation of: {rewritten_headline}"
                
                time.sleep(delay_between_requests)
                
                # Create image with defensive checks
                content_hash = self._generate_content_hash(headline, description)
                if not content_hash or len(content_hash) < 8:
                    logger.error(f"Generated content hash is too short: '{content_hash}' for headline '{headline}'")
                    content_hash = (content_hash + "00000000")[:8]
                
                image_filename = f"news_{content_hash[:8]}"
                
                # Additional defensive checks
                if not image_prompt or not image_prompt.strip():
                    logger.warning(f"Image prompt is empty for: {headline[:50]}...")
                    image_prompt = f"A visual representation of: {rewritten_headline}"
                
                if not image_filename or not image_filename.strip():
                    logger.error(f"Image filename is empty for: {headline[:50]}...")
                    image_filename = "news_unknown"
                
                logger.debug(f"Calling create_image with prompt: '{image_prompt[:60]}...', filename: '{image_filename}'")
                
                image_filepath = self.create_image(image_prompt, image_filename)
                
                if not image_filepath:
                    logger.warning(f"Failed to create image for: {headline[:50]}...")
                    image_filepath = "image_generation_failed"
                
                # Prepare data for master CSV
                master_data = {
                    'original_headline': headline,
                    'rewritten_headline': rewritten_headline,
                    'original_description': description,
                    'rewritten_description': rewritten_description,
                    'image_prompt': image_prompt,
                    'image_filepath': image_filepath,
                    'url': url,
                    'content_hash': content_hash,
                    'processed_date': pd.Timestamp.now().isoformat()
                }
                
                # Save all data
                self._save_to_master_csv(master_data)
                self._save_tracking_data(headline, description, url)
                
                processed_count += 1
                logger.info(f"✓ Successfully processed item {index}")
                
                time.sleep(delay_between_requests)
                
            except Exception as e:
                logger.error(f"Error processing item {index}: {e}. Headline: '{headline}', Description: '{description[:100]}...', URL: '{url}'")
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
        print(f"- Master CSV: {self.master_output_file}")
        print(f"- Images folder: {self.images_folder}")
        print(f"- Tracking data: {self.duplicate_tracking_file}")
        print(f"{'='*60}")

def main():
    """Main function to run the news processor"""
    print("Starting Enhanced News Processing System...")
    print("-" * 50)
    
    # Initialize processor
    processor = NewsProcessor()
    
    # Check if API keys are available
    if not processor.api_configs:
        logger.error("No API keys found in environment variables!")
        print("Please set one or more of these API keys in your .env file:")
        print("- API_KEY_1")
        print("- API_KEY_2") 
        print("- API_KEY_3")
        print("- API_KEY_4")
        print("- API_KEY_5")
        return
    
    print(f"Found {len(processor.api_configs)} API key(s) from different providers")
    
    # Process all news
    processor.process_all_news(delay_between_requests=2.0)

if __name__ == "__main__":
    main()
