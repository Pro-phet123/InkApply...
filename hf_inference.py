# hf_inference.py
import os
import requests

HF_TOKEN = os.getenv("HF_TOKEN")

# Using serverless inference — fastest available route
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
API_URL  = "https://router.huggingface.co/v1/chat/completions"


def query_llama3(prompt: str, retries: int = 2) -> str:
    if not HF_TOKEN:
        return "Error: HF_TOKEN not set. Add it to Railway Variables or Streamlit Secrets."

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
        "max_tokens": 700,  # slightly reduced for faster response
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=60,  # 60s max — fail fast instead of freezing for 3 mins
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            if attempt < retries:
                continue  # retry once silently
            return "Request timed out. The model is under heavy load — please try again in a moment."

        except requests.exceptions.RequestException as e:
            return f"API request failed: {e}"

    return "Failed to generate cover letter after retries. Please try again."
