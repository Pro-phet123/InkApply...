import os
import base64
from io import BytesIO

import streamlit as st
from PyPDF2 import PdfReader
from docx import Document

from prompts import generate_cover_letter_prompt
from hf_inference import query_llama3

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="InkApply – AI Cover Letter Generator",
    page_icon="Inkapply-logo.png",   # browser tab icon
    layout="wide",
)

# ---------------- GLOBAL STYLING ----------------
st.markdown("""
<style>
.block-container { padding-top: 2.5rem !important; max-width: 900px; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

section[data-testid="stSidebar"] { padding-top: 1rem; }
.sidebar-logo {
    display: flex;
    justify-content: center;
    padding: 0.75rem 0 1.25rem 0;
}
.sidebar-logo img {
    border-radius: 50%;
    width: 88px;
    height: 88px;
    object-fit: cover;
    border: 1px solid #2a2a2a;
}

textarea, input {
    background-color: #1f1f1f !important;
    border: 1px solid #2b2b2b !important;
    border-radius: 12px !important;
    padding: 0.75rem !important;
    color: #ffffff !important;
}
textarea::placeholder, input::placeholder {
    color: #9aa0a6 !important;
}
textarea:focus, input:focus {
    border-color: #10A37F !important;
    box-shadow: 0 0 0 1px rgba(16,163,127,0.45);
    outline: none !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR LOGO ----------------
logo_path = "Inkapply-logo.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" /></div>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown("### InkApply")

st.sidebar.markdown(
    "<p style='color:#9aa0a6; text-align:center;'>AI Resume & Cover Letter Generator</p>",
    unsafe_allow_html=True
)

# ---------------- HERO ----------------
st.markdown(
    "<h3 style='margin-bottom:0.25rem;'>AI Cover Letter Generator</h3>"
    "<p style='color:#9aa0a6; margin-top:0;'>Create tailored cover letters in seconds.</p>",
    unsafe_allow_html=True
)

# ---------------- HELPERS ----------------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

# ---------------- INPUTS ----------------
job_title = st.text_input(
    "",
    placeholder="Job title (e.g. Junior Software Developer)"
)

job_description = st.text_area(
    "",
    placeholder="Paste the job description here…",
    height=180
)

uploaded_file = st.file_uploader(
    "Upload your resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

# ---------------- RESUME HANDLING (WORKING LOGIC) ----------------
resume_text = ""

if uploaded_file is not None:
    st.success(f"Resume '{uploaded_file.name}' uploaded successfully ✅")

    try:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = extract_text_from_docx(uploaded_file)

        st.subheader("📄 Resume Preview")
        st.text_area(
            "Extracted resume content",
            value=resume_text,
            height=260
        )

    except Exception as e:
        st.error(f"Failed to read resume file: {e}")

# ---------------- OPTIONAL MANUAL RESUME ----------------
manual_resume = st.text_area(
    "Or paste your resume here (optional)",
    height=220,
    placeholder="Use this only if you didn’t upload a file"
)

final_resume = resume_text.strip() or manual_resume.strip()

# ---------------- GENERATE ----------------
if st.button("✨ Generate cover letter"):
    if not job_title.strip():
        st.warning("Please enter a job title.")
    elif not job_description.strip():
        st.warning("Please paste the job description.")
    elif not final_resume:
        st.warning("Please upload or paste your resume.")
    else:
        with st.spinner("Generating your cover letter…"):
            prompt = generate_cover_letter_prompt(
                job_title.strip(),
                job_description.strip(),
                final_resume
            )

            result = query_llama3(prompt)

        st.subheader("✉️ Your cover letter")
        st.text_area(
            "",
            value=result,
            height=360
        )

        # Downloads
        st.download_button(
            "Download TXT",
            result,
            "cover_letter.txt",
            "text/plain"
        )

        doc = Document()
        doc.add_heading(f"Cover Letter – {job_title}", 0)
        doc.add_paragraph(result)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            "Download Word (.docx)",
            buffer,
            "cover_letter.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
