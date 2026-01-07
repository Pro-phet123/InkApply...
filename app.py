import os
import base64
from io import BytesIO

import streamlit as st
from PyPDF2 import PdfReader
from docx import Document

from prompts import generate_cover_letter_prompt
from hf_inference import query_llama3


# ================= SESSION STATE INIT =================
st.session_state.setdefault("resume_bytes", None)
st.session_state.setdefault("resume_content", "")
st.session_state.setdefault("uploaded_file_name", "")
st.session_state.setdefault("resume_source", "none")  # upload | paste | none


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="InkApply – AI Resume & Cover Letter Generator",
    layout="wide",
)


# ================= GLOBAL STYLING =================
st.markdown("""
<style>
.block-container { padding-top: 2.75rem !important; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
textarea, input {
    background-color: #1f1f1f !important;
    border: 1px solid #2b2b2b !important;
    border-radius: 12px !important;
    padding: 0.75rem !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)


# ================= SIDEBAR =================
logo_path = "Inkapply-logo.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.sidebar.markdown(
        f'<div style="text-align:center"><img src="data:image/png;base64,{logo_base64}" width="90" style="border-radius:50%"/></div>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown("### InkApply")


# ================= HERO =================
st.markdown(
    "<h3>AI Cover Letter Generator</h3>"
    "<p style='color:#9aa0a6'>Create tailored cover letters in seconds.</p>",
    unsafe_allow_html=True
)


# ================= INPUTS =================
job_title = st.text_input(
    "Job title",
    placeholder="Senior Embedded Software Engineer",
    key="job_title"
)

job_description = st.text_area(
    "Job description",
    placeholder="Paste the job description here…",
    height=160,
    key="job_description"
)


# ================= FILE PARSER =================
def parse_uploaded_file(file_bytes: bytes, filename: str) -> str:
    try:
        if filename.lower().endswith(".pdf"):
            reader = PdfReader(BytesIO(file_bytes))
            return "\n".join(
                p.extract_text() for p in reader.pages if p.extract_text()
            ).strip()

        if filename.lower().endswith(".docx"):
            doc = Document(BytesIO(file_bytes))
            return "\n".join(
                p.text for p in doc.paragraphs if p.text.strip()
            ).strip()

        if filename.lower().endswith(".txt"):
            return file_bytes.decode("utf-8", errors="ignore").strip()

        return ""
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        return ""


# ================= FILE UPLOADER =================
uploaded_file = st.file_uploader(
    "Upload your resume (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"],
    key="resume_uploader"
)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()

    parsed_text = parse_uploaded_file(file_bytes, uploaded_file.name)

    if parsed_text:
        st.session_state.resume_bytes = file_bytes
        st.session_state.resume_content = parsed_text
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.resume_source = "upload"

        st.success(f"Resume loaded: {uploaded_file.name}")
    else:
        st.warning("Could not extract text from the file.")


# ================= RESUME PREVIEW =================
resume_label = "Resume content"
if st.session_state.uploaded_file_name:
    resume_label += f" (from {st.session_state.uploaded_file_name})"

resume_text = st.text_area(
    resume_label,
    value=st.session_state.resume_content,
    height=260,
    key="resume_editor"
)

# Detect manual edits
if resume_text != st.session_state.resume_content:
    st.session_state.resume_content = resume_text
    st.session_state.resume_source = "paste"


# ================= GENERATION =================
if st.button("Generate cover letter ✨"):
    if not job_title.strip():
        st.warning("Please enter a job title.")
    elif not st.session_state.resume_content.strip():
        st.warning("Please upload or paste your resume.")
    else:
        trimmed_resume = " ".join(st.session_state.resume_content.split()[:300])
        trimmed_desc = " ".join(job_description.split()[:200])

        prompt = generate_cover_letter_prompt(
            job_title.strip(),
            trimmed_desc,
            trimmed_resume
        )

        with st.spinner("Generating your cover letter…"):
            generated_text = query_llama3(prompt)

        st.markdown("### Your cover letter")
        st.write(generated_text)

        st.download_button(
            "Download TXT",
            generated_text,
            "cover_letter.txt",
            "text/plain"
        )

        doc = Document()
        doc.add_heading(f"Cover Letter – {job_title}", 0)
        doc.add_paragraph(generated_text)

        buf = BytesIO()
        doc.save(buf)
        buf.seek(0)

        st.download_button(
            "Download Word (.docx)",
            buf,
            "cover_letter.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
