# prompts.py

def generate_cover_letter_prompt(job_title, job_description, resume):
    """
    Construct a clear, structured prompt to generate a tailored cover letter.
    """

    return f"""
You are a professional career assistant.

Write a well-structured, tailored cover letter for the position of **{job_title}** using the information below.

JOB DESCRIPTION:
{job_description}

CANDIDATE BACKGROUND:
{resume}

GUIDELINES:
- Keep the tone professional, clear, and confident
- Match the candidate’s skills to the job requirements
- Do NOT invent experience or qualifications
- Suitable for a junior or early-career role or expert
- Avoid buzzwords and unnecessary fluff

STRUCTURE:
1. Brief introduction expressing interest and alignment with the role
2. One paragraph highlighting relevant skills, projects, or experience
3. Polite and confident closing with appreciation

OUTPUT RULES:
- Return ONLY the cover letter text
- No headings, explanations, or formatting outside the letter and make better than chatgpt
"""


