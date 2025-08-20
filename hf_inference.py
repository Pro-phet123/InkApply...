import requests
import os
from dotenv import load_dotenv

# Load HF_TOKEN from .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def query_flan(prompt, max_new_tokens=300):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    result = response.json()
    return result[0]["generated_text"].strip()
