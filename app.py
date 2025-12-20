# app.py
import os
import base64
from io import BytesIO
from docx import Document
import streamlit as st

from prompts import generate_cover_letter_prompt
from hf_inference import query_llama3  # Llama 3 API function


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="InkApply – AI Resume & Cover Letter Generator",
    layout="wide",
)


# --- GLOBAL STYLING ---
st.markdown("""
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
    width: 30vw;
    max-width: 130px;
    height: auto;
    object-fit: cover;
    border: 2px solid #2a2a2a;
}
</style>
""", unsafe_allow_html=True)


# --- SIDEBAR LOGO ---
logo_path = "Inkapply-logo.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode("utf-8")
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" /></div>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown("### InkApply")


# --- HERO TEXT ---
st.markdown(
    """
    #<h2>AI Resume & Cover Letter Generator</h2>
    <p style="color: #b3b3b3;">
        Quickly craft tailored documents for any job using AI.
    </p>
    """,
    unsafe_allow_html=True
)


# --- INPUTS (NO HEADER, PLACEHOLDER-LED) ---
job_title = st.text_input(
    label="",
    placeholder="Job title (e.g. Senior Embedded Software Engineer)"
)

job_description = st.text_area(
    label="",
    placeholder="Paste the job description here (optional but recommended)",
    height=160
)


# --- Helper: parse uploaded resume ---
def parse_uploaded_file(uploaded_file) -> str:
    try:
        raw = uploaded_file.read()
        name = uploaded_file.name.lower()
        bio = BytesIO(raw)

        if name.endswith(".pdf"):
            from PyPDF2 import PdfReader
            reader = PdfReader(bio)
            return "\n".join(
                p.extract_text() for p in reader.pages if p.extract_text()
            ).strip()

        elif name.endswith(".docx"):
            import docx
            doc = docx.Document(bio)
            return "\n".join(
                p.text for p in doc.paragraphs if p.text.strip()
            ).strip()

        elif name.endswith(".txt"):
            return raw.decode("utf-8", errors="ignore").strip()

        return ""

    except Exception:
        st.warning("Could not read the file. Please paste your resume instead.")
        return ""


# --- FILE UPLOADER ---
uploaded_file = st.file_uploader(
    label="Upload your resume (PDF preferred, DOCX/TXT supported)",
    type=["pdf", "docx", "txt"]
)

resume_content = ""

if uploaded_file:
    resume_content = parse_uploaded_file(uploaded_file)
    if resume_content:
        st.success("Resume loaded successfully.")
    else:
        st.warning("We couldn’t extract text. You can paste your resume below.")


# --- FALLBACK PASTE AREA ---
resume_content = st.text_area(
    label="",
    placeholder="Or paste your resume content here",
    value=resume_content,
    height=260
)


# --- GENERATE BUTTON ---
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

                # --- DOWNLOAD OPTIONS ---
                st.download_button(
                    "Download as TXT",
                    generated_text,
                    "cover_letter.txt",
                    "text/plain"
                )

                st.download_button(
                    "Download as Markdown",
                    generated_text,
                    "cover_letter.md",
                    "text/markdown"
                )

                doc = Document()
                doc.add_heading(f"Cover Letter – {job_title}", 0)
                doc.add_paragraph(generated_text)

                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)

                st.download_button(
                    "Download as Word (.docx)",
                    buffer,
                    "cover_letter.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            except Exception as e:
                st.error(f"Generation failed: {e}")
