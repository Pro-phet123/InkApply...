# prompts.py


def generate_cover_letter_prompt(job_title: str, job_description: str, resume: str) -> str:
    """
    Construct a highly specific, tailored prompt that produces
    a cover letter that feels human-written, not AI-generated.
    """

    return f"""
You are an expert career coach and professional writer who crafts cover letters that get interviews.

Your task: Write a highly specific, tailored cover letter for the position of {job_title}.

---
JOB DESCRIPTION:
{job_description}

CANDIDATE BACKGROUND:
{resume}

---

STRICT RULES — follow every one:

1. OPEN WITH IMPACT
   - Never start with "I am excited to apply" or "I am writing to apply"
   - Open with a confident statement that immediately connects the candidate's most relevant achievement or skill to the role
   - Example opening style: "Three years managing X taught me that Y — exactly the challenge [Company/Role] is solving."

2. BE HYPER-SPECIFIC
   - Reference actual skills, tools, technologies, or experiences from the resume
   - Reference actual requirements or keywords from the job description
   - Never use vague phrases like "strong background", "passionate about", "esteemed organization", "unique combination", or "I am confident"

3. SHOW, DON'T TELL
   - Instead of "I have strong Python skills" → say what was BUILT or ACHIEVED with Python
   - Instead of "I managed large-scale systems" → describe the scale, outcome, or impact

4. CONTACT & SIGN-OFF
   - Extract the candidate's full name from the resume and sign off with it
   - If the candidate's full name is NOT found, use the placeholder: [Your Full Name]
   - In the closing paragraph, include a contact line formatted exactly like this:
     "I can be reached at [email] or [phone number]."
   - If an email is found in the resume, use it — otherwise write the placeholder: [your.email@example.com]
   - If a phone number is found in the resume, use it — otherwise write the placeholder: [Your Phone Number]
   - If a LinkedIn URL or portfolio link is found in the resume, add it as: "LinkedIn: [url]"
   - If no LinkedIn or portfolio is found, add the placeholder: "LinkedIn: [Your LinkedIn URL]"
   - Close with "Sincerely," followed by the candidate's name or [Your Full Name]

5. LENGTH & TONE
   - 3 short paragraphs maximum — tight, confident, no fluff
   - Tone: direct, professional, human — not robotic or sycophantic
   - No buzzwords: avoid "leverage", "synergy", "dynamic", "passionate", "excited", "esteemed"

6. FORMAT
   - Plain text only — no markdown, no bullet points, no headings
   - Do NOT include a date, address block, or subject line
   - Return ONLY the cover letter — no explanations, no preamble

Write the cover letter now.
"""
