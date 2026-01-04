import os
import base64
from io import BytesIO

import streamlit as st
from PyPDF2 import PdfReader
import docx2txt
from docx import Document

from prompts import generate_cover_letter_prompt
from hf_inference import query_llama3


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="InkApply – AI Resume & Cover Letter Generator",
    layout="wide",
)


# ---------------- GLOBAL STYLING ----------------
st.markdown("""
<style>
.block-container {
    padding-top: 2.75rem !important;
}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

section[data-testid="stSidebar"] {
    padding-top: 1rem;
}

.sidebar-logo {
    display: flex;
    justify-content: center;
    padding: 0.5rem 0 1rem 0;
}

.sidebar-logo img {
    border-radius: 50%;
    width: 90px;
    height: 90px;
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


# ---------------- SIDEBAR ----------------
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


# ---------------- HERO ----------------
st.markdown(
    "<h3 style='margin-bottom:0.35rem;'>AI Cover Letter Generator</h3>"
    "<p style='color:#9aa0a6; margin-top:0;'>Create tailored cover letters in seconds.</p>",
    unsafe_allow_html=True
)


# ---------------- INPUTS ----------------
job_title = st.text_input(
    "",
    placeholder="Job title (e.g. Senior Embedded Software Engineer)"
)

job_description = st.text_area(
    "",
    placeholder="Paste the job description here (optional but recommended)",
    height=160
)


# ---------------- FILE PARSER (CLOUD SAFE) ----------------
def parse_uploaded_file(uploaded_file) -> str:
    try:
        filename = uploaded_file.name.lower()

        if filename.endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
            return "\n".join(text).strip()

        elif filename.endswith(".docx"):
            # Streamlit Cloud safe
            return docx2txt.process(uploaded_file).strip()

        elif filename.endswith(".txt"):
            return uploaded_file.read().decode("utf-8", errors="ignore").strip()

        return ""

    except Exception as e:
        st.error(f"Failed to read file: {e}")
        return ""


# ---------------- UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload your resume (PDF preferred, DOCX/TXT supported)",
    type=["pdf", "docx", "txt"]
)

# 🔴 DEBUG — DO NOT REMOVE UNTIL CONFIRMED WORKING
st.write("DEBUG uploaded_file:", uploaded_file)

resume_content = ""

if uploaded_file:
    resume_content = parse_uploaded_file(uploaded_file)
    if resume_content:
        st.success("Resume loaded successfully.")
    else:
        st.warning("Could not extract text. Please paste your resume below.")


# ---------------- MANUAL RESUME INPUT ----------------
resume_content = st.text_area(
    "",
    placeholder="Or paste your resume content here…",
    value=resume_content,
    height=260
)


# ---------------- GENERATION ----------------
if st.button("Generate cover letter ✨"):
    if not job_title.strip():
        st.warning("Please enter a job title.")
    elif not resume_content.strip():
        st.warning("Please upload or paste your resume.")
    else:
        trimmed_resume = " ".join(resume_content.split()[:300])
        trimmed_desc = " ".join((job_description or "").split()[:200])

        prompt = generate_cover_letter_prompt(
            job_title.strip(),
            trimmed_desc,
            trimmed_resume
        )

        with st.spinner("Generating your cover letter…"):
            try:
                generated_text = query_llama3(prompt)

                st.markdown("### Your cover letter")
                st.write(generated_text.strip())

                st.download_button(
                    "Download TXT",
                    generated_text,
                    "cover_letter.txt",
                    "text/plain"
                )

                doc = Document()
                doc.add_heading(f"Cover Letter – {job_title}", 0)
                doc.add_paragraph(generated_text)

                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)

                st.download_button(
                    "Download Word (.docx)",
                    buffer,
                    "cover_letter.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            except Exception as e:
                st.error(f"Generation failed: {e}")
