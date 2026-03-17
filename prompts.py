# prompts.py

def generate_cover_letter_prompt(job_title, job_description, resume):
    """
    Construct a clear, structured prompt to generate a tailored cover letter.
    Modelled on a real high-quality cover letter example.
    """

    return f"""
You are a professional career assistant and expert cover letter writer.

Write a well-structured, tailored cover letter for the position of {job_title} using the information below.

JOB DESCRIPTION:
{job_description}

CANDIDATE BACKGROUND:
{resume}

GUIDELINES:
- Keep the tone professional, clear, and confident
- Match the candidate's skills to the job requirements
- DO NOT invent experience or qualifications — use only what is in the resume
- Avoid buzzwords and unnecessary fluff
- Write as if a human career expert wrote this, not an AI

STRUCTURE — follow this exact order:

1. HEADER BLOCK (first lines of the letter):
   - Candidate's full name (Title Case) — extract from resume, or write: Your Full Name
   - Candidate's role/title line — extract from resume (e.g. Data Scientist | AI/ML Engineer), or write: Your Title
   - Contact line: email | phone | location — extract each from resume, use placeholders if missing:
     your.email@example.com | +000 000 000 0000 | Your City, Country
   - Today's date: write the current month and year (e.g. March 2026)
   - Then write: Hiring Manager
   - Then write: [Company Name]
   - Then write: [Company Address / Remote]
   - Then write the subject line: Re: Application for {job_title} Position

2. GREETING:
   Dear Hiring Manager,

3. OPENING PARAGRAPH:
   - Express strong interest in the {job_title} role
   - Immediately highlight the candidate's strongest qualification (degree, CGPA, key experience)
   - Mention 1–2 standout facts from the resume that are most relevant to the role
   - Do NOT start with "I am writing to apply" — open with confidence and substance

4. EXPERIENCE PARAGRAPH:
   - Describe the candidate's most relevant work experience in detail
   - Reference specific responsibilities, tools, or achievements from the resume
   - Show real impact — numbers, outcomes, or scale where available

5. PROJECTS / TECHNICAL SKILLS PARAGRAPH:
   - Highlight 2–3 projects or technical achievements from the resume most relevant to the role
   - Mention specific tools, models, accuracy rates, or outcomes
   - Connect these directly to what the job requires

6. SKILLS & CLOSING PARAGRAPH:
   - List key technical skills relevant to the role (languages, frameworks, tools, certifications)
   - Mention availability (full-time, remote, freelance) if stated in the resume
   - End with a warm, confident sentence inviting further discussion

7. SIGN-OFF:
   Thank you for your time and consideration.

   Yours sincerely,

   [Candidate full name in Title Case — extract from resume, or write: Your Full Name]

8. CONTACT BLOCK (after sign-off):
   - Email: extract from resume, or write: your.email@example.com
   - Phone: extract from resume, or write: +000 000 000 0000
   - GitHub: if username found, format as https://github.com/[username]; if full URL found use it; if none write: your GitHub URL
   - LinkedIn: extract URL from resume, or write: your LinkedIn URL
   Format plainly like this:
   email | phone
   GitHub: ... | LinkedIn: ...

OUTPUT RULES:
- Return ONLY the cover letter text — no explanations, no preamble, nothing after the contact block
- Plain text only — no markdown bold, no asterisks, no bullet points inside the letter
- Write better than ChatGPT — specific, human, and tailored
"""
