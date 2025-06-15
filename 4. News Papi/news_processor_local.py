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
import subprocess

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
    3. Rewrites headlines AND descriptions using local Ollama AI
    4. Generates image prompts and creates actual images
    5. Stores all processed data in a master CSV file
    6. Uses local Ollama models for text generation
    """
    
    def __init__(self):
        # Ollama configuration
        self.ollama_base_url = "http://localhost:11434"
        self.ollama_model = "llama3"  # Default model, can be changed
        
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
        
        # Check Ollama availability and models
        self._check_ollama_setup()
        self._load_existing_processed_data()
    
    def _check_ollama_setup(self) -> None:
        """Check if Ollama is running and has models available"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
                
                if available_models:
                    logger.info(f"Ollama is running. Available models: {available_models}")
                    
                    # Use the first available model or check if preferred model exists
                    if self.ollama_model not in available_models:
                        self.ollama_model = available_models[0]
                        logger.info(f"Using model: {self.ollama_model}")
                else:
                    logger.error("No models found in Ollama. Please pull a model first.")
                    logger.info("You can pull a model using: ollama pull llama3")
                    raise Exception("No Ollama models available")
            else:
                raise Exception("Ollama not responding")
                
        except requests.exceptions.RequestException:
            logger.error("Ollama is not running or not accessible at http://localhost:11434")
            logger.info("Please start Ollama by running: ollama serve")
            raise Exception("Ollama not available")
    
    def _get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = [line.split()[0] for line in lines if line.strip()]
                return models
            else:
                logger.warning("Could not get model list via CLI, using API")
                response = requests.get(f"{self.ollama_base_url}/api/tags")
                if response.status_code == 200:
                    models_data = response.json()
                    return [model['name'] for model in models_data.get('models', [])]
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
        return []
    
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
    
    def _make_ollama_request(self, prompt: str, system_message: str = "", max_retries: int = 3) -> Optional[str]:
        """Make request to local Ollama API"""
        for attempt in range(max_retries):
            try:
                # Combine system message and prompt
                full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
                
                payload = {
                    "model": self.ollama_model,
                    "prompt": full_prompt,
                    "stream": False  # Get complete response at once
                }
                
                response = requests.post(
                    f"{self.ollama_base_url}/api/generate",
                    json=payload,
                    timeout=180  # Longer timeout for local processing
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    content = response_data.get('response', '')
                    if content:
                        return content.strip()
                    else:
                        logger.error("Empty response from Ollama")
                        return None
                else:
                    logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed to Ollama (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            except Exception as e:
                logger.error(f"Unexpected error in Ollama request: {e}")
                
        return None
    
    def rewrite_headline(self, original_headline: str) -> Optional[str]:
        """Rewrite headline to make it more engaging using Ollama"""
        if not original_headline or not original_headline.strip():
            logger.warning("Empty headline provided for rewriting")
            return None
        
        system_message = (
            "You are a professional news editor. Rewrite headlines to make them more engaging and clickable. "
            "Keep them concise but compelling. Output only the headline as plain text, nothing else. "
            "Do not add quotes, explanations, or any other text."
        )
        
        prompt = f"Rewrite this headline: {original_headline}"
        
        rewritten = self._make_ollama_request(prompt, system_message)
        if rewritten:
            # Clean up any potential formatting
            rewritten = rewritten.strip().strip('"').strip("'")
            logger.info(f"Headline rewritten: {original_headline[:30]}... -> {rewritten[:30]}...")
        return rewritten
    
    def rewrite_description(self, original_description: str, headline: str) -> Optional[str]:
        """Rewrite description to make it more engaging using Ollama"""
        if not original_description or not original_description.strip():
            logger.warning("Empty description provided for rewriting")
            return None
        
        system_message = (
            "You are a professional news editor. Rewrite news descriptions to make them more engaging and informative. "
            "Keep the key facts but make them more compelling to read. Make it 2-3 sentences maximum. "
            "Output only the description as plain text, nothing else. Do not add quotes or explanations."
        )
        
        prompt = f"Context headline: {headline}\n\nRewrite this description: {original_description}"
        
        rewritten = self._make_ollama_request(prompt, system_message)
        if rewritten:
            # Clean up any potential formatting
            rewritten = rewritten.strip().strip('"').strip("'")
            logger.info(f"Description rewritten for: {headline[:30]}...")
        return rewritten
    
    def generate_image_prompt(self, headline: str, description: str) -> Optional[str]:
        """Generate image description prompt for the news using Ollama"""
        if not headline or not headline.strip():
            logger.warning("Empty headline provided for image prompt generation")
            return None
        
        system_message = (
            "You are an AI image prompt specialist. Create detailed image prompts for AI image generation based on news stories. "
            "The image should visually represent the story. Do not include text in the image description. "
            "Include Kenyan context where appropriate. Make it engaging and relatable. "
            "Output only the image prompt, nothing else. Do not add quotes or explanations."
        )
        
        news_content = f"Headline: {headline}\nDescription: {description or ''}"
        prompt = f"Create an image prompt for this news story:\n\n{news_content}"
        
        image_prompt = self._make_ollama_request(prompt, system_message)
        if image_prompt:
            # Clean up any potential formatting
            image_prompt = image_prompt.strip().strip('"').strip("'")
            logger.info(f"Image prompt generated for: {headline[:30]}...")
        return image_prompt
    
    def create_image(self, prompt: str, filename: str) -> Optional[str]:
        """Create image from prompt and save to file (unchanged - still uses URL)"""
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
    
    def set_model(self, model_name: str) -> bool:
        """Change the Ollama model being used"""
        available_models = self._get_available_models()
        if model_name in available_models:
            self.ollama_model = model_name
            logger.info(f"Switched to model: {model_name}")
            return True
        else:
            logger.error(f"Model {model_name} not available. Available models: {available_models}")
            return False
    
    def process_all_news(self, delay_between_requests: float = 1.0) -> None:
        """Process all news items - rewrite headlines, descriptions, and create images"""
        news_items = self.load_news_data()
        
        if not news_items:
            logger.error("No news items to process!")
            return
        
        new_items_count = 0
        processed_count = 0
        
        logger.info(f"Starting to process {len(news_items)} news items...")
        logger.info(f"Using Ollama model: {self.ollama_model}")
        
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
                # Rewrite headline using Ollama
                rewritten_headline = self.rewrite_headline(headline)
                if not rewritten_headline:
                    logger.warning(f"Failed to rewrite headline: {headline[:50]}...")
                    rewritten_headline = headline
                
                time.sleep(delay_between_requests)
                
                # Rewrite description using Ollama
                rewritten_description = self.rewrite_description(description, headline)
                if not rewritten_description:
                    logger.warning(f"Failed to rewrite description for: {headline[:50]}...")
                    rewritten_description = description
                
                time.sleep(delay_between_requests)
                
                # Generate image prompt using Ollama
                image_prompt = self.generate_image_prompt(rewritten_headline, rewritten_description)
                if not image_prompt:
                    logger.warning(f"Failed to generate image prompt for: {headline[:50]}...")
                    image_prompt = f"A visual representation of: {rewritten_headline}"
                
                time.sleep(delay_between_requests)
                
                # Create image with defensive checks (still uses URL service)
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
        print(f"Model used: {self.ollama_model}")
        print(f"{'='*60}")
        print(f"Output files:")
        print(f"- Master CSV: {self.master_output_file}")
        print(f"- Images folder: {self.images_folder}")
        print(f"- Tracking data: {self.duplicate_tracking_file}")
        print(f"{'='*60}")

def main():
    """Main function to run the news processor"""
    print("Starting Enhanced News Processing System with Ollama...")
    print("-" * 50)
    
    try:
        # Initialize processor
        processor = NewsProcessor()
        
        # Optionally change model if you want to use a different one
        # available_models = processor._get_available_models()
        # print(f"Available models: {available_models}")
        # processor.set_model("mistral")  # Uncomment to use a different model
        
        # Process all news
        processor.process_all_news(delay_between_requests=1.0)
        
    except Exception as e:
        logger.error(f"Failed to initialize or run processor: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Ollama is installed and running: ollama serve")
        print("2. Pull a model if you haven't: ollama pull llama3")
        print("3. Check if Ollama is accessible at http://localhost:11434")

if __name__ == "__main__":
    main()
