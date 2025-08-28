import streamlit as st
from prompts import generate_cover_letter_prompt
from hf_inference import query_flan
import os
import base64

# === PAGE CONFIG ===
st.set_page_config(
    page_title="InkApply – AI Resume & Cover Letter Generator",
    layout="wide"
)

# === STYLING ===
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        .sidebar-logo {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1em;
        }
        .sidebar-logo img {
            border-radius: 50%;
            width: 130px;
            height: 130px;
            object-fit: cover;
            border: 2px solid #ccc;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# === SIDEBAR LOGO ===
logo_path = "Inkapply-logo.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as img_file:
        logo_base64 = base64.b64encode(img_file.read()).decode("utf-8")
    st.sidebar