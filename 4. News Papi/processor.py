import requests
import json
import csv
import os
from dotenv import load_dotenv

load_dotenv()

# Access the environment variables
api_key = os.getenv('API_KEY')

prompt = input( "what do you wanna know?   ")
with open("news.csv", "r") as f:
    reader = csv.reader(f)

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": api_key,
    "Content-Type": "application/json",
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "deepseek/deepseek-r1-0528:free",
    "messages": [
      {
        "role": "user",
        "content": prompt
      }
    ],
    
  })
)


# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    response_data = response.json()  # This will convert the response to a Python dictionary
    
    if 'choices' in response_data:
        answer = response_data['choices'][0]['message']['content']
        with open('processed.csv', 'a', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([prompt, str(answer)])

        print("Response from the model:", answer)
else:
    print("Error:", response.status_code, response.text)