# hf_inference.py
import os
import requests

HF_TOKEN = os.getenv("HF_TOKEN")

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct:novita"
API_URL = "https://router.huggingface.co/v1/chat/completions"


def query_llama3(prompt: str) -> str:
    if not HF_TOKEN:
        return "Error: HF_TOKEN not set. Add it to Streamlit Secrets."

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional career assistant that writes clear, "
                    "concise, tailored cover letters based on a resume and job description."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
    }

    try:
        response = requests.post(
            API_URL, headers=headers, json=payload, timeout=180
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        return f"HF API request failed: {e}"
