# prompts.py

def generate_cover_letter_prompt(job_title, job_description, resume):
    """
    Construct a concise instruction for Flan-T5 to generate a tailored cover letter.
    """
    # Trim whitespace and ensure concise prompt
    return (
        f"Write a professional cover letter for the position of {job_title}.\n"
        f"Use the job description and candidate background below to customize the letter.\n\n"
        f"Job Description:\n{job_description}\n\n"
        f"Candidate Background:\n{resume}\n\n"
        f"The cover letter should include:\n"
        f"1. A brief introduction stating interest and role alignment.\n"
        f"2. A paragraph highlighting relevant skills and achievements.\n"
        f"3. A confident closing expressing gratitude and next steps.\n\n"
        f"Return only the cover letter text without headers or metadata."
    )
