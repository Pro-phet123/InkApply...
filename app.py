# app.py
import os
import base64
from io import BytesIO
from docx import Document
import streamlit as st

from prompts import generate_cover_letter_prompt
from hf_inference import query_llama3  # use the new Llama 3 API function

# --- PAGE CONFIG & STYLING ---
st.set_page_config(page_title="InkApply – AI Resume & Cover Letter Generator", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.sidebar-logo { display: flex; justify-content: center; align-items: center; padding: 1em; }
.sidebar-logo img { border-radius: 50%; width: 130px; height: 130px; object-fit: cover; border: 2px solid #ccc; }
</style>
""", unsafe_allow_html=True)

# Sidebar logo
logo_path = "Inkapply-logo.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode("utf-8")
    st.sidebar.markdown(f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" /></div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown("<h4>Logo not found</h4>", unsafe_allow_html=True)

st.markdown("**AI Resume & Cover Letter Generator**<br>Quickly craft tailored documents for any job using AI.", unsafe_allow_html=True)

# --- INPUT FIELDS ---
st.header("📥 Input Section")
job_title = st.text_input("Job Title (e.g. Senior Embedded Software Engineer)")
job_description = st.text_area("Paste the Job Description", height=160)

# --- Helper: parse uploaded file robustly ---
def parse_uploaded_file(uploaded_file) -> str:
    try:
        raw = uploaded_file.read()
        name = uploaded_file.name.lower()
        bio = BytesIO(raw)
        if name.endswith(".pdf"):
            from PyPDF2 import PdfReader
            reader = PdfReader(bio)
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()]).strip()
        elif name.endswith(".docx"):
            import docx
            doc = docx.Document(bio)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()]).strip()
        elif name.endswith(".txt"):
            return raw.decode("utf-8", errors="ignore").strip()
        else:
            return ""
    except Exception:
        st.warning("⚠️ Could not parse uploaded file. Please paste your resume instead.")
        return ""

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("📄 Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
resume_content = ""

if uploaded_file:
    st.info(f"📂 Selected: {uploaded_file.name} — {uploaded_file.size} bytes")
    resume_content = parse_uploaded_file(uploaded_file)
    if resume_content:
        st.success("✅ Resume loaded from file.")
    else:
        st.warning("⚠️ Could not extract readable text from the file. You can paste below.")

resume_content = st.text_area("Or Paste Your Resume Content", value=resume_content, height=260)

# --- GENERATE COVER LETTER ---
if st.button("✨ Generate Cover Letter"):
    if not job_title.strip():
        st.warning("⚠️ Please fill in the Job Title.")
    elif not resume_content.strip():
        st.warning("⚠️ Please fill in the Resume Content (paste or upload).")
    else:
        # Trim text for better AI performance
        trimmed_resume = " ".join(resume_content.split()[:300])
        trimmed_desc = " ".join((job_description or "").split()[:200])
        prompt = generate_cover_letter_prompt(job_title.strip(), trimmed_desc, trimmed_resume)

        with st.spinner("🖊️ Generating your cover letter — this may take a few seconds..."):
            try:
                generated_text = query_llama3(prompt)
                st.subheader("📄 Generated Cover Letter")
                st.write(generated_text.strip())

                # --- TXT DOWNLOAD ---
                st.download_button(
                    "⬇️ Download as TXT",
                    data=generated_text.strip(),
                    file_name="cover_letter.txt",
                    mime="text/plain"
                )

                # --- Markdown DOWNLOAD ---
                st.download_button(
                    "⬇️ Download as MD",
                    data=generated_text.strip(),
                    file_name="cover_letter.md",
                    mime="text/markdown"
                )

                # --- Word (.docx) DOWNLOAD ---
                doc = Document()
                doc.add_heading(f"Cover Letter: {job_title.strip()}", 0)
                doc.add_paragraph(generated_text.strip())
                word_buffer = BytesIO()
                doc.save(word_buffer)
                word_buffer.seek(0)
                st.download_button(
                    "⬇️ Download as Word (.docx)",
                    data=word_buffer,
                    file_name="cover_letter.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            except Exception as e:
                st.error(f"❌ Generation failed: {e}")
