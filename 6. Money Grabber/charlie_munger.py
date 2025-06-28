import os
from dotenv import load_dotenv
import MetaTrader5 as mt5
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome

driver.quit()

if not mt5.initialize():
    print("could not connect to metatrader")

rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_H1, 99, 100)
print(f"{rates[85:95]}")
print("")

load_dotenv()

api_key = os.environ.get("API_KEY")

question = "can you analyse the following request for me for the EURUSD and rank if i should close a deal from 0 to 1  ,  1 being  i should make  a deal and 0 being i should not , and the type of deal that i should make; example output: buy 0.7, sell 0.2 only output the output that i have given you"
response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": api_key,
    "Content-Type": "application/json",
  },
    data=json.dumps({
      "model": "qwen/qwen3-235b-a22b:free",
      "messages": [
        {
          "role": "user",
          "content": question+ str(rates[85:95])
        }
      ],      
    })
  )
# Check for success
if response.status_code == 200:
    # Parse JSON
    response_json = response.json()
    # Extract the assistant's reply (adjust path based on actual response structure)
    try:
        reply = response_json['choices'][0]['message']['content']
        print("Assistant reply:", reply)
        # If you want to use the reply as a string
        reply_string = str(reply)
        with open('response.md', 'w') as f:
            f.write( reply_string)
    except KeyError:
        print("Could not find reply in response:", response_json)
else:
    print("Error:", response.status_code, response.text)