import requests
import json
import csv
import os
from dotenv import load_dotenv

load_dotenv()
def ask(prompt):
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
         "content": "Rewrite this headline to make it more engaging(output only the headline as plain text, nothing else please!!!!)(if you put anything else my program will crash and please no recommendations just the renovated headlines in plain text)(this is the headline):"+prompt
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

def pic_prompt(prompt):
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
         "content": "Think like an expert,Describe an image that would visually represent this news. My ai model does not render text well so do not include image descriptions of text. This is also a kenyan website so try to include a kenyan context not so much but slightly. Make the users to be able to connect with the image(Output only the description, nothing else please, Treat every prompt as separate and please dont output anything else other than the prompt in plain text):"+prompt
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
        with open('prompts.csv', 'a', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([str(answer)])

        print("Response from the model:", answer)
  else:
     print("Error:", response.status_code, response.text)




# Access the environment variables
api_key = os.getenv('API_KEY')

def ask_p():
  os.remove("processed.csv")
  with open("news.csv", "r", newline="") as f:
      reader = csv.reader(f)
      for row in reader:
          ask(str(row))

def pic_prompt_p():
  os.remove("prompts.csv")
  with open("processed.csv", "r", newline="") as f:
      reader = csv.reader(f)
      for row in reader:
          pic_prompt(str(row)) 

#ask_p()
pic_prompt_p()
