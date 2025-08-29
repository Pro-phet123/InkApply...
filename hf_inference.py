# hf_inference.py
import os
import requests

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct:fireworks-ai"
API_URL = "https://router.huggingface.co/v1/chat/completions"

def query_llama3(prompt: str) -> str:
    """
    Query Llama 3.1 via Hugging Face chat completion API.
    Returns the AI-generated text.
    """
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN not set. Add it to Streamlit Secrets.")
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False  # set True for streaming if desired
    }
    
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=180)
    
    if resp.status_code != 200:
        raise Exception(f"HF API Error {resp.status_code}: {resp.text}")
    
    data = resp.json()
    return data["choices"][0]["message"]["content"]
