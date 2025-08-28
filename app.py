import streamlit as st
import os
import base64
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

from prompts import generate_cover_letter_prompt  # your prompt function

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
st.markdown(
    "**AI Resume & Cover Letter Generator**<br>Quickly craft tailored documents for any job using AI.",
    unsafe_allow_html=True
)

# === INPUT SECTION ===
st.header("📥 Input Section")
job_title = st.text_input("Job Title (e.g. Junior Data Scientist)")
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

        if resume_content:
            st.success("✅ Resume loaded successfully!")
        else:
            st.warning("⚠️ No readable text found. Paste your resume below.")

    except Exception as e:
        st.error(f"❌ Error reading uploaded file: {e}")

# --- FALLBACK TEXT AREA (preserves uploaded or typed content) ---
resume_content = st.text_area("Or Paste Your Resume Content", value=resume_content, height=250)

# === LOAD FLAN-T5 MODEL (cached for performance) ===
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
    return pipeline("text2text-generation", model=model, tokenizer=tokenizer)

generator = load_model()

# === GENERATE COVER LETTER ===
if st.button("✨ Generate Cover Letter"):
    if not job_title.strip() or not resume_content.strip():
        st.warning("⚠️ Please fill in both the Job Title and Resume Content.")
    else:
        def trim_words(text, max_words=200):
            return " ".join(text.split()[:max_words])

        trimmed_resume = trim_words(resume_content, 200)
        trimmed_description = trim_words(job_description, 100)
        prompt = generate_cover_letter_prompt(job_title, trimmed_description, trimmed_resume)

        try:
            result = generator(prompt, max_new_tokens=350)
            generated_letter = result[0]['generated_text']
            st.subheader("📄 Generated Cover Letter")
            st.write(generated_letter.strip())
        except Exception as e:
            st.error(f"❌ Error generating cover letter: {e}")
