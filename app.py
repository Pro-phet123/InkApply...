import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from prompts import generate_cover_letter_prompt
import os
import base64
import requests

# === PAGE CONFIG ===
st.set_page_config(
    page_title="InkApply – AI Resume & Cover Letter Generator",
    layout="wide"
)

# === STYLING ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.sidebar-logo { display: flex; justify-content: center; align-items: center; padding: 1em; }
.sidebar-logo img { border-radius: 50%; width: 130px; height: 130px; object-fit: cover; border: 2px solid #ccc; }
</style>
""", unsafe_allow_html=True)

# === SIDEBAR LOGO ===
logo_path = "Inkapply-logo.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as img_file:
        logo_base64 = base64.b64encode(img_file.read()).decode("utf-8")
    st.sidebar.markdown(f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" /></div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown("<h4>Logo not found</h4>", unsafe_allow_html=True)

# === HEADER ===
st.markdown("**AI Resume & Cover Letter Generator**<br>Quickly craft tailored documents for any job using AI.", unsafe_allow_html=True)

# === INPUT SECTION ===
st.header("📥 Input Section")
job_title = st.text_input("Job Title (e.g. Data Scientist)")
job_description = st.text_area("Paste the Job Description", height=150)

# === FILE UPLOADER ===
uploaded_file = st.file_uploader("📄 Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
resume_content = ""

if uploaded_file:
    try:
        fname = uploaded_file.name.lower()
        if fname.endswith(".pdf"):
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            resume_content = "\n".join([p.extract_text() or "" for p in reader.pages]).strip()
        elif fname.endswith(".docx"):
            import docx
            doc = docx.Document(uploaded_file)
            resume_content = "\n".join([p.text for p in doc.paragraphs if p.text.strip()]).strip()
        elif fname.endswith(".txt"):
            resume_content = uploaded_file.read().decode("utf-8").strip()

        if not resume_content:
            st.warning("⚠️ No readable text found. Paste your resume below.")
            resume_content = st.text_area("Or Paste Your Resume Content", height=250)
        else:
            st.success("✅ Resume loaded successfully!")
    except Exception as e:
        st.error(f"❌ Error reading uploaded file: {e}")
        resume_content = st.text_area("Or Paste Your Resume Content", height=250)
else:
    resume_content = st.text_area("Or Paste Your Resume Content", height=250)

# === MODEL LOADING (LOCAL OR API FALLBACK) ===
USE_API = os.getenv("HF_TOKEN") is not None  # If you set HF_TOKEN in Streamlit Cloud secrets

@st.cache_resource
def load_local_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
        generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)
        return generator
    except Exception as e:
        st.warning(f"⚠️ Local model failed to load: {e}")
        return None

generator = None
if not USE_API:
    generator = load_local_model()
    if generator:
        st.info("✅ Using local model for generation")
    else:
        st.warning("⚠️ Falling back to Hugging Face Inference API. Set HF_TOKEN in secrets.")

# === HUGGING FACE INFERENCE API FUNCTION ===
def query_hf_api(prompt: str) -> str:
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        raise ValueError("❌ HF_TOKEN not set. Cannot call Hugging Face API.")
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 350}}
    response = requests.post("https://api-inference.huggingface.co/models/google/flan-t5-base", headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")
    data = response.json()
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]
    return str(data)

# === GENERATE COVER LETTER ===
if st.button("✨ Generate Cover Letter"):
    if not job_title or not resume_content.strip():
        st.warning("⚠️ Please fill in both the Job Title and Resume Content.")
    else:
        def trim_words(text, max_words=200):
            return " ".join(text.split()[:max_words])

        trimmed_resume = trim_words(resume_content, 200)
        trimmed_description = trim_words(job_description, 100)
        prompt = generate_cover_letter_prompt(job_title, trimmed_description, trimmed_resume)

        try:
            if generator:
                # Local model
                result = generator(prompt, max_length=350, truncation=True)
                generated_letter = result[0]["generated_text"]
            else:
                # API fallback
                generated_letter = query_hf_api(prompt)
            st.subheader("📄 Generated Cover Letter")
            st.write(generated_letter.strip())
        except Exception as e:
            st.error(f"❌ Error generating cover letter: {e}")
