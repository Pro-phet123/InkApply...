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
    try:
        with open(logo_path, "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        st.sidebar.markdown(
            f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" /></div>',
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.sidebar.error(f"⚠️ Error loading logo: {e}")
else:
    st.sidebar.markdown("<h4>Logo not found</h4>", unsafe_allow_html=True)

# === HEADER ===
st.markdown(
    "**AI Resume & Cover Letter Generator**<br>"
    "Quickly craft tailored documents for any job using artificial intelligence.",
    unsafe_allow_html=True,
)

# === INPUT SECTION ===
st.header("📥 Input Section")

job_title = st.text_input("Job Title (e.g. Junior Data Scientist)")
job_description = st.text_area("Paste the Job Description", height=150)

# === FILE UPLOADER WITH DEBUG ===
uploaded_file = st.file_uploader("📄 Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
resume_content = ""

# Debug logging to see if Streamlit detects the file
if uploaded_file:
    st.info(f"📂 File detected: {uploaded_file.name} ({uploaded_file.size} bytes, {uploaded_file.type})")
else:
    st.info("📂 No file selected yet.")

# === FILE HANDLING ===
if uploaded_file:
    try:
        file_name = uploaded_file.name.lower()

        if file_name.endswith(".pdf"):
            from PyPDF2 import PdfReader
            pdf_reader = PdfReader(uploaded_file)
            resume_content = "\n".join(
                [page.extract_text() or "" for page in pdf_reader.pages]
            ).strip()

        elif file_name.endswith(".docx"):
            from docx import Document
            uploaded_file.seek(0)
            doc = Document(uploaded_file)
            resume_content = "\n".join(
                [p.text for p in doc.paragraphs if p.text.strip()]
            ).strip()

        elif file_name.endswith(".txt"):
            resume_content = uploaded_file.read().decode("utf-8").strip()

        if resume_content:
            st.success("✅ Resume loaded successfully from uploaded file.")
        else:
            st.warning("⚠️ No readable text found in your resume. Please paste it below.")
            resume_content = st.text_area("Or Paste Your Resume Content", height=250)

    except Exception as e:
        st.error(f"❌ Error reading uploaded file: {e}")
        resume_content = st.text_area("Or Paste Your Resume Content", height=250)
else:
    resume_content = st.text_area("Or Paste Your Resume Content", height=250)

# === GENERATE COVER LETTER ===
if st.button("✨ Generate Cover Letter"):
    if not job_title or not resume_content.strip():
        st.warning("⚠️ Please fill in both the Job Title and Resume Content.")
    else:
        def trim_words(text, max_words=200):
            words = text.split()
            return " ".join(words[:max_words])

        trimmed_resume = trim_words(resume_content, 200)
        trimmed_description = trim_words(job_description, 100)
        prompt = generate_cover_letter_prompt(job_title, trimmed_description, trimmed_resume)

        try:
            generated_letter = query_flan(prompt)
            st.subheader("📄 Generated Cover Letter")
            st.write(generated_letter.strip())
        except Exception as e:
            st.error(f"❌ Error generating cover letter: {e}")
