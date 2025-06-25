import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("API_KEY")
def prompt():
    message = input("Enter message:  ")
    if message.lower() == "quit":
        return
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": api_key,
        "Content-Type": "application/json",
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    data=json.dumps({
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
        {
            "role": "user",
            "content": "You are a messaging bot from the terminal, please output only plain text, here is the message from the user: Do not format this is not an md document, !!!only text"+message
        }
        ],
        
    })
    )
    if response.status_code == 200:
    # Parse the JSON response
        response_data = response.json()  # This will convert the response to a Python dictionary

        if 'choices' in response_data:
            answer = response_data['choices'][0]['message']['content']
        
            print("\033[33mResponse:", answer, "\033[0m")
            prompt()
    else:
        print("Error:", response.status_code, response.text)

prompt()
