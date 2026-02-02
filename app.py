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
    page_icon="📝",
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
    border-radius: 12px;
    width: 120px;
    height: auto;
    object-fit: contain;
}

textarea, input {
    background-color: #1f1f1f !important;
    border: 1px solid #2b2b2b !important;
    border-radius: 12px !important;
    padding: 0.75rem !important;
    color: #ffffff !important;
}
            
            /* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

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

# ---------------- SIDEBAR WITH LOGO ---------------- 
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

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("Generate professional, tailored cover letters using AI.")

# ---------------- HERO ---------------- 
st.markdown(
    "<h3 style='margin-bottom:0.35rem;'>AI Cover Letter Generator</h3>"
    "<p style='color:#9aa0a6; margin-top:0;'>Create tailored cover letters in seconds.</p>",
    unsafe_allow_html=True
)

# ---------------- HELPER FUNCTIONS ---------------- 
def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    try:
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        st.error(f"Failed to read DOCX: {e}")
        return ""

# ---------------- INPUTS ---------------- 
job_title = st.text_input(
    "",
    placeholder="Job title (e.g. Senior Software Engineer)",
    key="job_title_input"
)

job_description = st.text_area(
    "",
    placeholder="Paste the job description here...",
    height=160,
    key="job_desc_input"
)

# ---------------- FILE UPLOADER ---------------- 
uploaded_file = st.file_uploader(
    "Upload your resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

# ---------------- RESUME HANDLING ---------------- 
resume_text = ""

if uploaded_file is not None:
    st.success(f"Resume '{uploaded_file.name}' uploaded successfully ✅")
    
    try:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = extract_text_from_docx(uploaded_file)
        
        # Show preview immediately
        if resume_text:
            st.markdown("#### 📄 Resume Preview")
            st.text_area(
                "Extracted Resume Content",
                value=resume_text,
                height=250,
                key="resume_preview",
                disabled=True
            )
    except Exception as e:
        st.error(f"Failed to read resume file: {e}")

# ---------------- OPTIONAL MANUAL OVERRIDE ---------------- 
manual_resume = st.text_area(
    "Or paste your resume here (optional)",
    height=200,
    placeholder="Only use this if you didn't upload a file",
    key="manual_resume_input"
)

# Prefer uploaded resume
final_resume = resume_text.strip() or manual_resume.strip()

# ---------------- GENERATE BUTTON ---------------- 
if st.button("Generate cover letter ✨", type="primary"):
    if not job_title.strip():
        st.warning("⚠️ Please provide a job title.")
    elif not job_description.strip():
        st.warning("⚠️ Please provide a job description.")
    elif not final_resume:
        st.warning("⚠️ Please upload a resume or paste one.")
    else:
        with st.spinner("Generating your cover letter..."):
            try:
                prompt = generate_cover_letter_prompt(
                    job_title.strip(),
                    job_description.strip(),
                    final_resume
                )
                
                result = query_llama3(prompt)
                
                st.markdown("---")
                st.markdown("### ✉️ Your Cover Letter")
                st.text_area(
                    "",
                    value=result,
                    height=350,
                    key="generated_cover_letter"
                )
                
                # Download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        "📥 Download TXT",
                        result,
                        "cover_letter.txt",
                        "text/plain"
                    )
                
                with col2:
                    # Create DOCX
                    doc = Document()
                    doc.add_heading(f"Cover Letter – {job_title}", 0)
                    doc.add_paragraph(result)
                    buffer = BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)
                    
                    st.download_button(
                        "📥 Download DOCX",
                        buffer,
                        "cover_letter.docx",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                
            except Exception as e:
                st.error(f"❌ Generation failed: {e}")