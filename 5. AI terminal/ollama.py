import requests
response = requests.post(     
"http://localhost:11434/api/generate",
json={ 
"model": "llama2-uncensored",
"prompt": "Hello",
"stream": False  # Disable streaming
} )
print(response.json()["response"])

import subprocess

# Run a command and capture its output
result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)

print("Command output:")
print(result.stdout)
