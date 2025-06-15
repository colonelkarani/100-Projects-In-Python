from PIL import Image, ImageDraw, ImageFont

# Open the image
img = Image.open("image.png")

# Create a Draw object
draw = ImageDraw.Draw(img)

# Load a font
font_path = "Rye-Regular.ttf"  # Replace with your font path
font_size = 30
font = ImageFont.truetype(font_path, font_size)

# Define the headline and position
headline = "Breaking News: Major Event Happens!"
position = (0, 0)  # (x, y) coordinates

# Choose text color
text_color = (129, 254, 72)  

# Add the text to the image
draw.text(position, headline, fill=text_color, font=font)

  # Draw a rectangle behind the text
text_width, text_height = draw.textbbox(headline, font=font)
rectangle_position = (position[0] - 10, position[1] - 10, position[0] + text_width + 10, position[1] + text_height + 10)
draw.rectangle(rectangle_position, fill=(0, 0, 0, 128))  # Semi-transparent black

# Save or show the image
img.show()  # To display the image
img.save("news_image_with_headline2.jpg")  # To save the image