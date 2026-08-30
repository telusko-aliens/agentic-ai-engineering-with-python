
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key=os.getenv("OPENAI_API_KEY")

url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json", 
    "Authorization": f"Bearer {api_key}"
}
payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": "What is AI in short"
        }

    ]
}

response=requests.post(
    url,
    headers=headers,
    json=payload
)
print("-----------------------------------------")
# print(response.json()["choices"][0]["message"]["content"])
print("-----------------------------------------")
print(response.json())
