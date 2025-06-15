import csv
from PIL import Image, ImageDraw, ImageFont
import os

# Define paths
input_csv = 'processed_news_master.csv'  # Your CSV file path
input_img_dir = './generated_images/'  # Folder containing input images
output_img_dir = 'output_images'  # Folder to save output images

# Create output directory if it doesn't exist
os.makedirs(output_img_dir, exist_ok=True)

def add_text_to_image(image_path, text, output_path):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        width, height = img.size

        # Calculate max width for text (with some padding)
        max_text_width = width * 0.95

        # Start with a reasonable font size
        font_size = 40
        font_path = "arial.ttf"
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            # Fallback to default PIL font if arial.ttf is not found
            font = ImageFont.load_default()

        # Get text dimensions using textbbox
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Reduce font size if text is too wide
        while text_width > max_text_width and font_size > 10:
            font_size -= 2
            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

        # Position text at bottom center with some padding
        x = (width - text_width) / 2
        y = height - text_height - 20  # 20 pixels from bottom

        # Draw a semi-transparent black rectangle behind text for readability
        rectangle_height = text_height + 20
        rectangle_y0 = y - 10
        rectangle_y1 = y + rectangle_height - 10
        draw.rectangle([(0, rectangle_y0), (width, rectangle_y1)], fill=(0, 0, 0, 180))

        # Draw text in white
        draw.text((x, y), text, font=font, fill=(255, 255, 255))

        # Save output image
        img.save(output_path)
        print(f"Processed: {image_path} -> {output_path}")

# Read CSV and process images
try:
    with open(input_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Debug: Print column names to identify the issue
        print("Available columns in CSV:")
        print(reader.fieldnames)
        
        # Check if the expected columns exist
        expected_columns = ['image_filepath', 'rewritten_headline']
        missing_columns = [col for col in expected_columns if col not in reader.fieldnames]
        
        if missing_columns:
            print(f"Missing columns: {missing_columns}")
            print("Please check your CSV file column names.")
            exit()
        
        for row in reader:
            # Try different possible column names for image file
            image_file = None
            for possible_name in ['image_filepath', 'image_file', 'filename', 'image_name']:
                if possible_name in row and row[possible_name]:
                    image_file = row[possible_name]
                    break
            
            # Try different possible column names for headline
            headline = None
            for possible_name in ['rewritten_headline', 'headline', 'new_headline', 'title']:
                if possible_name in row and row[possible_name]:
                    headline = row[possible_name]
                    break
            
            if not image_file:
                print("No image file column found in this row")
                continue
                
            if not headline or not headline.strip():
                print(f"No headline found for {image_file}")
                continue
                
            input_path = os.path.join(input_img_dir, image_file)
            output_path = os.path.join(output_img_dir, image_file)

            if os.path.exists(input_path):
                add_text_to_image(input_path, headline, output_path)
            else:
                print(f"Image file not found: {input_path}")

    print("Processing complete!")
    
except FileNotFoundError:
    print(f"CSV file '{input_csv}' not found. Please check the file path.")
except KeyError as e:
    print(f"Column not found in CSV: {e}")
    print("Please check that your CSV has the correct column names.")
except Exception as e:
    print(f"An error occurred: {e}")
