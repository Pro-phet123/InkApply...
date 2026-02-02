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
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------- FUTURISTIC CHATGPT-STYLE UI ----------------
st.markdown("""
<style>
/* Import modern font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global styling */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Dark futuristic background */
.stApp {
    background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
    background-attachment: fixed;
}

/* Main container - ChatGPT style centered */
.block-container {
    max-width: 750px !important;
    padding: 3rem 1.5rem !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Sidebar minimal styling */
section[data-testid="stSidebar"] {
    background: rgba(15, 20, 40, 0.95);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px);
}

/* Hero section - futuristic */
h1, h2, h3 {
    color: #ffffff !important;
}

/* Custom hero styling */
.hero-container {
    text-align: center;
    padding: 2rem 0 3rem 0;
    margin-bottom: 2rem;
}

.hero-icon {
    font-size: 56px;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 20px rgba(16, 163, 127, 0.5));
}

.hero-title {
    font-size: 42px !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #10A37F 0%, #1fc8a0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.75rem !important;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    font-size: 18px !important;
    color: rgba(255, 255, 255, 0.55) !important;
    font-weight: 400;
    line-height: 1.6;
}

/* Section headers */
.section-header {
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 2rem 0 1rem 0 !important;
    opacity: 0.7;
}

/* Text inputs - ChatGPT style */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.4rem !important;
    color: #ffffff !important;
    font-size: 17px !important;
    font-weight: 400 !important;
    min-height: 58px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.stTextInput > div > div > input:hover {
    border-color: rgba(16, 163, 127, 0.5) !important;
    background: rgba(255, 255, 255, 0.09) !important;
    box-shadow: 0 6px 20px rgba(16, 163, 127, 0.15);
}

.stTextInput > div > div > input:focus {
    border-color: #10A37F !important;
    background: rgba(255, 255, 255, 0.09) !important;
    box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.2), 0 8px 24px rgba(16, 163, 127, 0.2) !important;
    outline: none !important;
}

/* Text areas - larger and modern */
.stTextArea > div > div > textarea {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.4rem !important;
    color: #ffffff !important;
    font-size: 16px !important;
    font-weight: 400 !important;
    line-height: 1.65 !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.stTextArea > div > div > textarea:hover {
    border-color: rgba(16, 163, 127, 0.5) !important;
    background: rgba(255, 255, 255, 0.09) !important;
    box-shadow: 0 6px 20px rgba(16, 163, 127, 0.15);
}

.stTextArea > div > div > textarea:focus {
    border-color: #10A37F !important;
    background: rgba(255, 255, 255, 0.09) !important;
    box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.2), 0 8px 24px rgba(16, 163, 127, 0.2) !important;
    outline: none !important;
}

/* Placeholder text */
input::placeholder, textarea::placeholder {
    color: rgba(255, 255, 255, 0.35) !important;
    font-size: 16px !important;
    font-weight: 400 !important;
}

/* File uploader - modern card style */
.stFileUploader {
    margin: 1.5rem 0 !important;
}

.stFileUploader > label {
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    margin-bottom: 0.75rem !important;
}

.stFileUploader > div > div {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 2px dashed rgba(255, 255, 255, 0.2) !important;
    border-radius: 16px !important;
    padding: 2.5rem 2rem !important;
    text-align: center !important;
    transition: all 0.3s ease !important;
}

.stFileUploader > div > div:hover {
    background: rgba(255, 255, 255, 0.06) !important;
    border-color: rgba(16, 163, 127, 0.5) !important;
}

/* Generate button - prominent ChatGPT style */
.stButton > button {
    background: linear-gradient(135deg, #10A37F 0%, #0d8c6a 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 1.15rem 2.5rem !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin: 2rem 0 !important;
    min-height: 58px !important;
    width: 100% !important;
    box-shadow: 0 4px 16px rgba(16, 163, 127, 0.3), 0 8px 32px rgba(16, 163, 127, 0.15) !important;
    letter-spacing: 0.3px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0d8c6a 0%, #0a6b51 100%) !important;
    box-shadow: 0 6px 24px rgba(16, 163, 127, 0.4), 0 12px 48px rgba(16, 163, 127, 0.25) !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Download buttons - sleek modern style */
.stDownloadButton > button {
    background: rgba(255, 255, 255, 0.08) !important;
    color: rgba(255, 255, 255, 0.9) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.8rem !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    margin: 0.75rem 0.5rem 0.75rem 0 !important;
    transition: all 0.25s ease !important;
}

.stDownloadButton > button:hover {
    background: rgba(255, 255, 255, 0.12) !important;
    border-color: #10A37F !important;
    box-shadow: 0 4px 12px rgba(16, 163, 127, 0.2) !important;
}

/* Alert messages - modern cards */
.stAlert {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.5rem !important;
    font-size: 15px !important;
    margin: 1.5rem 0 !important;
    backdrop-filter: blur(10px);
}

/* Success alert */
.stSuccess {
    background: rgba(16, 163, 127, 0.12) !important;
    border-color: rgba(16, 163, 127, 0.4) !important;
}

/* Warning alert */
.stWarning {
    background: rgba(255, 193, 7, 0.12) !important;
    border-color: rgba(255, 193, 7, 0.4) !important;
}

/* Error alert */
.stError {
    background: rgba(244, 67, 54, 0.12) !important;
    border-color: rgba(244, 67, 54, 0.4) !important;
}

/* Info alert */
.stInfo {
    background: rgba(33, 150, 243, 0.12) !important;
    border-color: rgba(33, 150, 243, 0.4) !important;
}

/* Labels */
label {
    color: rgba(255, 255, 255, 0.75) !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    margin-bottom: 0.6rem !important;
}

/* Spinner - themed */
.stSpinner > div {
    border-color: #10A37F transparent transparent transparent !important;
}

/* Divider */
hr {
    border-color: rgba(255, 255, 255, 0.1) !important;
    margin: 2.5rem 0 !important;
}

/* Spacing */
.stTextInput, .stTextArea, .stFileUploader {
    margin-bottom: 1.5rem !important;
}

/* Output section styling */
.output-section {
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Subheaders */
h3 {
    font-size: 24px !important;
    font-weight: 600 !important;
    margin: 2rem 0 1.25rem 0 !important;
    color: rgba(255, 255, 255, 0.95) !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.03);
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.25);
}
</style>
""", unsafe_allow_html=True)

# ---------------- HERO SECTION ----------------
st.markdown("""
<div class="hero-container">
    <div class="hero-icon">✨</div>
    <h1 class="hero-title">InkApply</h1>
    <p class="hero-subtitle">Transform your resume into tailored cover letters with AI precision</p>
</div>
""", unsafe_allow_html=True)

# ---------------- HELPER FUNCTIONS (FIXED) ----------------
def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file bytes"""
    try:
        pdf_file = BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        raise Exception(f"PDF reading error: {str(e)}")

def extract_text_from_docx(file_bytes):
    """Extract text from DOCX file bytes"""
    try:
        docx_file = BytesIO(file_bytes)
        doc = Document(docx_file)
        text_parts = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
        return "\n".join(text_parts).strip()
    except Exception as e:
        raise Exception(f"DOCX reading error: {str(e)}")

# ---------------- JOB DETAILS SECTION ----------------
st.markdown('<p class="section-header"> Job Details</p>', unsafe_allow_html=True)

job_title = st.text_input(
    "Job Title",
    placeholder="e.g., Senior Product Designer, Software Engineer, Marketing Manager",
    key="job_title_input",
    label_visibility="collapsed"
)

job_description = st.text_area(
    "Job Description",
    placeholder="Paste the complete job description here...\n\nInclude requirements, responsibilities, and qualifications for best results.",
    height=240,
    key="job_desc_input",
    label_visibility="collapsed"
)

# ---------------- RESUME SECTION ----------------
st.markdown('<p class="section-header"> Your Resume</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Resume (PDF or DOCX)",
    type=["pdf", "docx"],
    help="Drag and drop or click to upload your resume",
    key="resume_uploader",
    label_visibility="collapsed"
)

# ---------------- FILE PROCESSING (FIXED) ----------------
resume_text = ""

if uploaded_file is not None:
    st.success(f"✅ '{uploaded_file.name}' uploaded successfully!")
    
    try:
        # Read file bytes
        file_bytes = uploaded_file.getvalue()
        
        # Process based on file type
        if uploaded_file.name.endswith('.pdf'):
            resume_text = extract_text_from_pdf(file_bytes)
        elif uploaded_file.name.endswith('.docx'):
            resume_text = extract_text_from_docx(file_bytes)
        else:
            st.error("❌ Unsupported file format")
        
        # Show preview if text extracted
        if resume_text:
            with st.expander("📝 Preview Extracted Resume", expanded=False):
                st.text_area(
                    "Resume Content",
                    value=resume_text,
                    height=300,
                    key="resume_preview",
                    disabled=True,
                    label_visibility="collapsed"
                )
        else:
            st.warning("⚠️ No text extracted. Your PDF might be image-based or empty.")
            
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("💡 Try: Check if PDF is password-protected or contains selectable text")

# ---------------- MANUAL INPUT OPTION ----------------
st.markdown('<p class="section-header" style="margin-top: 2.5rem;">Or paste your resume text</p>', unsafe_allow_html=True)

manual_resume = st.text_area(
    "Manual Resume Input",
    height=220,
    placeholder="If file upload didn't work, paste your resume content here...",
    key="manual_resume_input",
    label_visibility="collapsed"
)

# Determine final resume text
final_resume = resume_text.strip() or manual_resume.strip()

# ---------------- GENERATE BUTTON ----------------
generate_clicked = st.button("✨ Generate Cover Letter", use_container_width=True, type="primary")

if generate_clicked:
    # Validation
    if not job_title.strip():
        st.warning("⚠️ Please enter a job title")
    elif not job_description.strip():
        st.warning("⚠️ Please paste the job description")
    elif not final_resume:
        st.warning("⚠️ Please upload your resume or paste the text")
    else:
        # Generate cover letter
        with st.spinner("🤖 Crafting your personalized cover letter..."):
            try:
                prompt = generate_cover_letter_prompt(
                    job_title.strip(),
                    job_description.strip(),
                    final_resume
                )
                
                result = query_llama3(prompt)
                
                # Display output section
                st.markdown('<div class="output-section">', unsafe_allow_html=True)
                st.markdown("### ✉️ Your Cover Letter")
                
                st.text_area(
                    "Generated Cover Letter",
                    value=result,
                    height=450,
                    key="cover_letter_output",
                    label_visibility="collapsed"
                )
                
                # Download options
                st.markdown("#### 💾 Download")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        "📄 Download as TXT",
                        data=result,
                        file_name=f"cover_letter_{job_title.replace(' ', '_')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col2:
                    # Create Word document
                    doc = Document()
                    doc.add_heading(f"Cover Letter – {job_title}", 0)
                    doc.add_paragraph(result)
                    
                    buffer = BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)
                    
                    st.download_button(
                        "📝 Download as DOCX",
                        data=buffer,
                        file_name=f"cover_letter_{job_title.replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Generation failed: {str(e)}")
                st.info("💡 Try refreshing the page and trying again")

# ---------------- FOOTER ----------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: rgba(255, 255, 255, 0.3); font-size: 13px;'>Powered by AI • InkApply © 2024</p>",
    unsafe_allow_html=True
)