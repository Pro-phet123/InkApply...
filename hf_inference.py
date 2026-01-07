import os
import requests

HF_TOKEN = os.getenv("HF_TOKEN")

MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def query_llama3(prompt: str) -> str:
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN not set. Add it to Streamlit Secrets.")

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 700,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=180)

    if response.status_code != 200:
        return f"HF Error {response.status_code}: {response.text}"

    data = response.json()

    # HF returns list of generated texts
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]

    return str(data)
