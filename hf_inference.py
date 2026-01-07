# hf_inference.py
import os
import requests

# Load Hugging Face API token from environment or Streamlit secrets
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct:novita"  # deployed model
API_URL = "https://api-inference.huggingface.co/v1/chat/completions"

def query_llama3(prompt: str) -> str:
    """
    Query the deployed Llama 3 'novita' model via Hugging Face API.
    Returns the AI-generated text as a string.
    """
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN not set. Add it to Streamlit Secrets.")
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False  # True if you want streaming output
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        # Debug-friendly error
        print(f"HF API request failed: {e}")
        return f"Error: {e}"
