import streamlit as st
from prompts import generate_cover_letter_prompt
from hf_inference import query_llama3
from PyPDF2 import PdfReader
from docx import Document

st.set_page_config(
    page_title="InkApply – AI Cover Letter Generator",
    page_icon="📝",
    layout="centered"
)

st.title("📝 AI Cover Letter Generator")
st.caption("Upload your resume or paste it below. Both work independently.")

# -----------------------------
# Helpers
# -----------------------------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

# -----------------------------
# Inputs
# -----------------------------
job_title = st.text_input("Job Title", placeholder="e.g. Junior Software Developer")

job_description = st.text_area(
    "Job Description",
    height=220,
    placeholder="Paste the job description here..."
)

uploaded_file = st.file_uploader(
    "Upload your resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

# -----------------------------
# Resume handling (KEY FIX)
# -----------------------------
resume_text = ""

if uploaded_file is not None:
    st.success(f"Resume '{uploaded_file.name}' uploaded successfully ✅")

    try:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = extract_text_from_docx(uploaded_file)

        # Show preview immediately
        st.subheader("📄 Resume Preview (auto-filled)")
        st.text_area(
            "Extracted Resume Content",
            value=resume_text,
            height=250,
            key="resume_preview"
        )

    except Exception as e:
        st.error(f"Failed to read resume file: {e}")

# -----------------------------
# Optional manual override
# -----------------------------
manual_resume = st.text_area(
    "Or paste your resume here (optional)",
    height=200,
    placeholder="Only use this if you didn’t upload a file"
)

# Prefer uploaded resume
final_resume = resume_text.strip() or manual_resume.strip()

# -----------------------------
# Generate
# -----------------------------
if st.button("🚀 Generate Cover Letter"):
    if not job_title or not job_description:
        st.warning("Please provide both job title and job description.")
    elif not final_resume:
        st.warning("Please upload a resume or paste one.")
    else:
        with st.spinner("Generating your cover letter..."):
            prompt = generate_cover_letter_prompt(
                job_title,
                job_description,
                final_resume
            )

            result = query_llama3(prompt)

        st.subheader("✉️ Generated Cover Letter")
        st.text_area(
            "Your Cover Letter",
            value=result,
            height=350
        )
