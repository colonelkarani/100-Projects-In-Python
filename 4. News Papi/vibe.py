import requests
import json
import csv

prompt = input("what do you wanna know? ")

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        # Remove or replace the following if not needed:
        # "HTTP-Referer": "<YOUR_SITE_URL>",
        # "X-Title": "<YOUR_SITE_NAME>",
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

if response.status_code == 200:
    response_data = response.json()
    if 'choices' in response_data and response_data['choices']:
        answer = response_data['choices'][0]['message']['content']
        with open('processed.csv', 'a', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([prompt, str(answer)])
        print("Response from the model:", answer)
    else:
        print("No choices found in response:", response_data)
else:
    print("Error:", response.status_code, response.text)
