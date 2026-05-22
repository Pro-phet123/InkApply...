# InkApply

##### ✍️ InkApply — AI Cover Letter Generator (ATS-Optimized)

<p align="center">
  <img src="Inkapply-logo.png" alt="InkApply Logo" width="260"/>
</p>

<p align="center">
  <b>An AI system that transforms job descriptions and user experience into structured, ATS-friendly cover letters tailored for each application.</b>
</p>

---

## Problem

Writing a strong cover letter for every job application is:

- Time-consuming  
- Difficult to personalize effectively  
- Often misaligned with ATS and recruiter expectations  
- Repetitive and inconsistent across applications  

Most AI tools generate generic letters that lack role specificity.

---

## 💡 Solution

**InkApply** is a focused AI system designed exclusively for generating **job-specific, structured, and ATS-aligned cover letters**.

It converts:

> User experience + Job description → Personalized, recruiter-ready cover letter

Each output is optimized for:
- Role relevance  
- Keyword alignment  
- Professional tone  
- Hiring-system readability (ATS compatibility)

---

## ⚙️ Key Features

###  Role-Specific Cover Letter Generator  
Generates fully structured cover letters tailored to a specific job description and role.

###  Job Description Intelligence Layer  
Extracts key hiring signals from job postings, including:
- Required skills  
- Core responsibilities  
- Recruiter priority keywords  

###  Context-Aware Writing Engine  
Ensures each cover letter reflects:
- User experience relevance  
- Job-specific alignment  
- Professional storytelling flow  

###  ATS Optimization Engine  
Rewrites content to improve keyword matching and recruiter filtering systems.

###  Streamlit Interface  
Simple, fast interface for generating and editing cover letters in real time.

---

## 🏗 System Architecture

```text
User Input (Experience + Job Description)
        ↓
Text Preprocessing (NLP cleanup)
        ↓
Job Description Signal Extraction
        ↓
Prompt Construction Engine (Role-specific template)
        ↓
Hugging Face Transformer Model
        ↓
Post-processing Layer:
    - Formatting structure
    - Keyword alignment
    - Tone refinement
        ↓
Streamlit UI Output (Editable Cover Letter)

```
## Run Locally

#### 1. Clone repository
```bash
git clone https://github.com/your-username/InkApply.git

```


#### 2. Enter project folder
  
```bash
cd InkApply

```

#### 3. Create virtual environment
```bash
python -m venv venv
```

#### 4a. Activate virtual environment(windows)
```bash
venv\Scripts\activate
```

#### 4b. Activate virtual environment(mac/linux)
```bash
source venv/bin/activate
```

#### 5. Install dependencies
```bash
pip install -r requirements.txt
```
#### 6. Run the application
```bash
streamlit run app.py
```

## 🌐 Live Demo

[Launch Web App](https://inkapply-cover-letter.streamlit.app/)
