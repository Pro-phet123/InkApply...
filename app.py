import os
import base64
from io import BytesIO

import streamlit as st
from PyPDF2 import PdfReader
from docx import Document

from prompts import generate_cover_letter_prompt
from hf_inference import query_llama3


# ================= PAGE CONFIG (MUST BE FIRST) =================
st.set_page_config(
    page_title="InkApply – AI Resume & Cover Letter Generator",
    layout="wide",
)


# ================= SESSION STATE (initialize safe defaults) =================
if "resume_bytes" not in st.session_state:
    st.session_state.resume_bytes = None

# resume_content is the internal stored resume (finalized when Generate is pressed)
if "resume_content" not in st.session_state:
    st.session_state.resume_content = ""

# uploaded_file_name guards re-parsing
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""

# resume_editor is directly bound to the text_area widget (UI source of truth)
# It will be set when a file is uploaded or when the user pastes/edits text
if "resume_editor" not in st.session_state:
    st.session_state.resume_editor = st.session_state.resume_content or ""


# ================= GLOBAL STYLING =================
st.markdown(
    """
<style>
.block-container { padding-top: 2.75rem !important; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
section[data-testid="stSidebar"] { padding-top: 1rem; }
.sidebar-logo { display: flex; justify-content: center; padding: 0.5rem 0 1rem 0; }
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
textarea::placeholder, input::placeholder { color: #9aa0a6 !important; }
textarea:focus, input:focus {
    border-color: #10A37F !important;
    box-shadow: 0 0 0 1px rgba(16,163,127,0.45);
    outline: none !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# ================= SIDEBAR =================
logo_path = "Inkapply-logo.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.sidebar.markdown(
        f'<div class="sidebar-logo"><img src="data:image/png;base64,{logo_base64}" /></div>',
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown("### InkApply")


# ================= HERO =================
st.markdown(
    "<h3 style='margin-bottom:0.35rem;'>AI Cover Letter Generator</h3>"
    "<p style='color:#9aa0a6; margin-top:0;'>Create tailored cover letters in seconds.</p>",
    unsafe_allow_html=True,
)


# ================= INPUTS =================
# Note: keep these outside form so they are immediately available
job_title = st.text_input("", placeholder="Job title (e.g. Senior Embedded Software Engineer)")

job_description = st.text_area(
    "",
    placeholder="Paste the job description here (optional but recommended)",
    height=160,
)


# ================= FILE PARSER =================
def parse_uploaded_file(file_bytes: bytes, filename: str) -> str:
    """Return text from PDF, DOCX, or TXT in a Streamlit Cloud-safe way."""
    try:
        if filename.lower().endswith(".pdf"):
            reader = PdfReader(BytesIO(file_bytes))
            pages = []
            for p in reader.pages:
                text = p.extract_text()
                if text:
                    pages.append(text)
            return "\n".join(pages).strip()

        if filename.lower().endswith(".docx"):
            doc = Document(BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
            return "\n".join(paragraphs).strip()

        if filename.lower().endswith(".txt"):
            return file_bytes.decode("utf-8", errors="ignore").strip()

    except Exception as e:
        # Use st.error for user-facing error, but do not crash
        st.error(f"Failed to read file: {e}")

    return ""


# ================= FILE UPLOADER (CHATGPT-STYLE, robust) =================
uploaded_file = st.file_uploader(
    "Upload your resume (PDF preferred, DOCX/TXT supported)",
    type=["pdf", "docx", "txt"],
)

# Parse ONLY when a NEW file is uploaded (guard by filename)
if uploaded_file and uploaded_file.name != st.session_state.uploaded_file_name:
    # getvalue() is stable across reruns
    try:
        file_bytes = uploaded_file.getvalue()
    except Exception:
        file_bytes = uploaded_file.read()  # fallback (rare)

    parsed_text = parse_uploaded_file(file_bytes, uploaded_file.name)

    if parsed_text:
        # update both internal stored resume and the text_area editor
        st.session_state.resume_bytes = file_bytes
        st.session_state.resume_content = parsed_text
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.resume_editor = parsed_text  # populate the UI editor immediately
        st.success(f"Resume '{uploaded_file.name}' loaded successfully!")
    else:
        st.warning("Could not extract text from the uploaded file. Please paste your resume below.")


# ================= MANUAL / PREVIEW INPUT =================
# Bind the text_area directly to session_state.resume_editor (UI value)
# This prevents the common overwrite problem because the widget controls its value
resume_label = "Resume content" + (
    f" (from {st.session_state.uploaded_file_name})" if st.session_state.uploaded_file_name else ""
)

# NOTE: using key makes Streamlit persist the text area across reruns automatically
st.text_area(label=resume_label, value=st.session_state.get("resume_editor", ""), key="resume_editor", height=260, placeholder="Or paste your resume content here…")

# DO NOT unconditionally overwrite internal resume_content here.
# We'll take the editor value when the user clicks Generate (or we can sync on explicit action).


# ================= GENERATE COVER LETTER =================
# When Generate is clicked, read the editor value, validate, then update resume_content and call LLM.
if st.button("Generate cover letter ✨"):
    # Pull the visible editor content (what the user sees/edited)
    editor_text = st.session_state.get("resume_editor", "") or ""
    editor_text = editor_text.strip()

    # If editor is empty but we previously had parsed resume_content (rare), fallback to that
    if not editor_text and st.session_state.get("resume_content", "").strip():
        editor_text = st.session_state.resume_content.strip()

    # Validation
    if not job_title.strip():
        st.warning("Please enter a job title.")
    elif not editor_text:
        st.warning("Please upload or paste your resume.")
    else:
        # Update internal stored resume to the latest editor text (user's final resume)
        st.session_state.resume_content = editor_text

        trimmed_resume = " ".join(st.session_state.resume_content.split()[:300])
        trimmed_desc = " ".join((job_description or "").split()[:200])

        prompt = generate_cover_letter_prompt(job_title.strip(), trimmed_desc, trimmed_resume)

        with st.spinner("Generating your cover letter…"):
            try:
                generated_text = query_llama3(prompt)
                if isinstance(generated_text, bytes):
                    generated_text = generated_text.decode("utf-8", errors="ignore")
                generated_text = (generated_text or "").strip()

                st.markdown("### Your cover letter")
                st.write(generated_text)

                # TXT download
                st.download_button("Download TXT", generated_text, "cover_letter.txt", "text/plain")

                # DOCX download
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
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

            except Exception as e:
                st.error(f"Generation failed: {e}")