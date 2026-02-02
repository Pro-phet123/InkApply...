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
    page_icon="Inkapply-logo.png",
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar always open by default
)

# ---------------- GLOBAL STYLING ----------------
st.markdown("""
<style>
/* Main container - more spacious */
.block-container { 
    padding-top: 3rem !important; 
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}

/* Font styling */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
    font-size: 16px !important;
}

/* Sidebar styling - expanded by default */
section[data-testid="stSidebar"] { 
    padding-top: 1.5rem;
    min-width: 280px !important;
}

.sidebar-logo {
    display: flex;
    justify-content: center;
    padding: 1rem 0 1.5rem 0;
}

.sidebar-logo img {
    border-radius: 50%;
    width: 100px;
    height: 100px;
    object-fit: cover;
    border: 2px solid #2a2a2a;
}

/* Larger text inputs and text areas */
.stTextInput > div > div > input {
    background-color: #1f1f1f !important;
    border: 1px solid #2b2b2b !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    color: #ffffff !important;
    font-size: 17px !important;
    min-height: 56px !important;
}

.stTextArea > div > div > textarea {
    background-color: #1f1f1f !important;
    border: 1px solid #2b2b2b !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    color: #ffffff !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
}

/* Placeholder text */
input::placeholder, textarea::placeholder {
    color: #9aa0a6 !important;
    font-size: 16px !important;
}

/* Focus states */
input:focus, textarea:focus {
    border-color: #10A37F !important;
    box-shadow: 0 0 0 2px rgba(16,163,127,0.25) !important;
    outline: none !important;
}

/* File uploader styling */
.stFileUploader {
    padding: 1.5rem 0 !important;
}

.stFileUploader > div > div {
    background-color: #1f1f1f !important;
    border: 2px dashed #2b2b2b !important;
    border-radius: 12px !important;
    padding: 2rem !important;
}

.stFileUploader label {
    font-size: 16px !important;
    font-weight: 600 !important;
    margin-bottom: 1rem !important;
}

/* Button styling - larger */
.stButton > button {
    background-color: #10A37F !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 1rem 2.5rem !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    margin-top: 1.5rem !important;
    min-height: 56px !important;
}

.stButton > button:hover {
    background-color: #0d8c6a !important;
    box-shadow: 0 4px 12px rgba(16,163,127,0.3) !important;
}

/* Download buttons */
.stDownloadButton > button {
    background-color: #2b2b2b !important;
    color: white !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 10px !important;
    padding: 0.85rem 1.75rem !important;
    font-size: 15px !important;
    margin-right: 1rem !important;
    margin-top: 1rem !important;
}

.stDownloadButton > button:hover {
    background-color: #3a3a3a !important;
    border-color: #10A37F !important;
}

/* Success/Warning/Error messages - larger */
.stAlert {
    padding: 1.25rem !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    margin: 1.5rem 0 !important;
}

/* Subheaders */
h3 {
    font-size: 28px !important;
    margin-bottom: 0.5rem !important;
}

/* Spacing between elements */
.stTextInput, .stTextArea, .stFileUploader {
    margin-bottom: 1.75rem !important;
}

/* Labels */
label {
    font-size: 15px !important;
    font-weight: 600 !important;
    margin-bottom: 0.75rem !important;
}

/* Spinner */
.stSpinner > div {
    border-color: #10A37F !important;
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
    "<p style='color:#9aa0a6; text-align:center; font-size:15px;'>AI Resume & Cover Letter Generator</p>",
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='color:#7a7a7a; font-size:13px; text-align:center;'>Upload your resume and job description to generate a tailored cover letter.</p>",
    unsafe_allow_html=True
)

# ---------------- HERO ----------------
st.markdown(
    "<h3 style='margin-bottom:0.5rem;'>AI Cover Letter Generator</h3>"
    "<p style='color:#9aa0a6; margin-top:0; font-size:17px;'>Create tailored cover letters in seconds.</p>",
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file using bytes"""
    try:
        pdf_file = BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_bytes):
    """Extract text from DOCX file using bytes"""
    try:
        docx_file = BytesIO(file_bytes)
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")

# ---------------- INPUTS ----------------
st.markdown("### 📋 Job Details")

job_title = st.text_input(
    "Job Title",
    placeholder="e.g. Junior Software Developer",
    key="job_title_input"
)

job_description = st.text_area(
    "Job Description",
    placeholder="Paste the full job description here…",
    height=220,
    key="job_desc_input"
)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📄 Your Resume")

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"],
    help="Supported formats: PDF and DOCX",
    key="resume_uploader"
)

# ---------------- RESUME HANDLING (FIXED) ----------------
resume_text = ""

if uploaded_file is not None:
    st.success(f"✅ Resume '{uploaded_file.name}' uploaded successfully!")

    try:
        # Read the file bytes
        file_bytes = uploaded_file.read()
        
        # Reset the file pointer for potential re-reading
        uploaded_file.seek(0)
        
        # Extract text based on file type
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(file_bytes)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx(file_bytes)
        else:
            st.error("Unsupported file format. Please upload a PDF or DOCX file.")
        
        if resume_text:
            st.markdown("#### 📝 Resume Preview")
            st.text_area(
                "Extracted content from your resume",
                value=resume_text,
                height=280,
                key="resume_preview",
                disabled=True
            )
        else:
            st.warning("⚠️ No text could be extracted from the uploaded file. Please check if your resume contains readable text.")

    except Exception as e:
        st.error(f"❌ Failed to read resume file: {str(e)}")
        st.info("💡 Tip: Make sure your PDF is not password-protected and contains selectable text (not just images).")

# ---------------- OPTIONAL MANUAL RESUME ----------------
st.markdown("<br>", unsafe_allow_html=True)

manual_resume = st.text_area(
    "Or paste your resume text here (optional)",
    height=260,
    placeholder="Use this field only if you didn't upload a file above…",
    key="manual_resume_input"
)

final_resume = resume_text.strip() or manual_resume.strip()

# ---------------- GENERATE ----------------
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    generate_button = st.button("✨ Generate Cover Letter", use_container_width=True)

if generate_button:
    if not job_title.strip():
        st.warning("⚠️ Please enter a job title.")
    elif not job_description.strip():
        st.warning("⚠️ Please paste the job description.")
    elif not final_resume:
        st.warning("⚠️ Please upload or paste your resume.")
    else:
        with st.spinner("🤖 Generating your personalized cover letter…"):
            prompt = generate_cover_letter_prompt(
                job_title.strip(),
                job_description.strip(),
                final_resume
            )

            result = query_llama3(prompt)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### ✉️ Your Cover Letter")
        
        st.text_area(
            "",
            value=result,
            height=420,
            key="cover_letter_output"
        )

        # Download buttons
        st.markdown("#### 💾 Download Options")
        
        col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 2])
        
        with col_dl1:
            st.download_button(
                "📄 Download TXT",
                result,
                "cover_letter.txt",
                "text/plain",
                use_container_width=True
            )

        with col_dl2:
            # Create Word document
            doc = Document()
            doc.add_heading(f"Cover Letter – {job_title}", 0)
            doc.add_paragraph(result)
            
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                "📝 Download Word",
                buffer,
                "cover_letter.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )