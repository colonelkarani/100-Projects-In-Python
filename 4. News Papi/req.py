import requests
import urllib.parse
from PIL import Image

prompt = input("What image do you want to create:  ")
name = input("What do you want to name your image:  ")
encoded_prompt = urllib.parse.quote(prompt)
url = "https://image.pollinations.ai/prompt/" + encoded_prompt

response = requests.get(url)
filename = name + ".png"
with open(filename, "wb") as f:
    f.write(response.content)

# Open and display the image automatically
img = Image.open(filename)
img.show()
