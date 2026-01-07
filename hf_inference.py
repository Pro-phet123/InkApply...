# hf_inference.py
import os
from openai import OpenAI

# Load Hugging Face API token from environment or Streamlit secrets
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct:novita"  # use the working deployment

# Initialize the OpenAI-compatible client for Hugging Face
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

def query_llama3(prompt: str) -> str:
    """
    Query Llama 3.1 via Hugging Face OpenAI-compatible API.
    Returns the AI-generated text as a string.
    """
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN not set. Add it to Streamlit Secrets.")
    
    # Send prompt to Llama 3
    completion = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract the generated text
    return completion.choices[0].message.content
