import requests

API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct"  # Replace 'gpt2' with your chosen model
API_TOKEN = "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"  # Replace with your Hugging Face access token

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

data = {
    "inputs": "Once upon a time in Kenya,"  # Your prompt or input
}

response = requests.post(API_URL, headers=headers, json=data)

if response.status_code == 200:
    print(response.json())
else:
    print("Error:", response.status_code, response.text)
