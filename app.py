import os, requests, streamlit as st

st.write("HF_TOKEN present?", bool(os.getenv("HF_TOKEN")))

def test_hf():
    token = os.getenv("HF_TOKEN")
    if not token:
        st.write("HF_TOKEN not found in environment.")
        return
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-base",
            headers=headers,
            json={"inputs": "Write one short sentence saying hello."},
            timeout=30
        )
        st.write("Status:", r.status_code)
        st.write("Response (truncated):", str(r.text)[:500])
    except Exception as e:
        st.write("Request error:", e)

if st.button("Run HF token test"):
    test_hf()
