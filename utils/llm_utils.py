import os
import json
from groq import Groq
from dotenv import load_dotenv
import re



load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


def analyze_resume(resume, jd):
    prompt = f"""
You are an AI Resume Analyzer.

Analyze resume vs job description.

Instructions:
- Score each relevant point out of 5
- Use ✅ ⚠️ ❌
- End with: SUGGESTIONS TO IMPROVE YOUR RESUME

Resume:
{resume}

Job Description:
{jd}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content


def generate_resume(name, email, phone, role, skills, experience, education):
    prompt = f"""
Create a PROFESSIONAL ATS FRIENDLY RESUME in plain text format (NO MARKDOWN, NO BOLD FORMATTING).

FORMAT EXACTLY:

{name.upper()}
{email} | {phone}

{role}

SUMMARY
2-3 lines professional summary.

SKILLS
Frontend: skill1, skill2, skill3
Backend: skill4, skill5, skill6
Other: skill7, skill8

EXPERIENCE
Company Name | Timeline (e.g., 2020-2023)
• Specific achievement or responsibility
• Another key accomplishment
• Technical contribution

Another Company Name | Timeline
• Achievement 1
• Achievement 2

EDUCATION
Bachelor's Degree in Computer Science | University Name

(Only include the degree and university. Do NOT include graduation dates, GPA, coursework, or other details.)

IMPORTANT:
- Use PLAIN TEXT only
- NO ** or bold formatting anywhere
- Use • bullet points ONLY for individual experience achievements
- Company names and timelines should be plain text (no bullets)
- Education section: ONLY degree and university name
- Do not add notes or disclaimers
- Keep role as a single line before SUMMARY
- Summary should be upon summary

Skills to organize: {skills}
Experience details: {experience}
Education details: {education}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a professional resume writer. Generate PLAIN TEXT resumes with no markdown formatting."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    resume_text = response.choices[0].message.content
    # Remove any ** bold formatting
    resume_text = resume_text.replace("**", "")
    return resume_text


def extract_resume_fields(resume_text):
    prompt = f"""
Extract the following fields from the resume text and return ONLY valid JSON with keys: name, email, phone, skills, experience, education.

- `name`: string
- `email`: string
- `phone`: string
- `skills`: string with skills organized by category like "Frontend: React, Vue\\nBackend: Node, Django\\nOther: Python, SQL"
- `experience`: string (can be multiple lines, separate companies with double newline)
- `education`: string (separate entries with double newline)

Resume:
{resume_text}

Return ONLY JSON, no markdown or extra text.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a JSON extractor. Output ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )

    content = response.choices[0].message.content.strip()

    # Clean markdown if any
    content = re.sub(r"```json|```", "", content).strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: simple heuristic extraction
        data = {}
        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text)
        if email_match:
            data["email"] = email_match.group(0)

        phone_match = re.search(r"(\+?\d[\d\-\s]{7,}\d)", resume_text)
        if phone_match:
            data["phone"] = phone_match.group(0).strip()

        # name: first non-empty line
        lines = [l.strip() for l in resume_text.splitlines() if l.strip()]
        if lines:
            data["name"] = lines[0]

        # skills
        skills_match = re.search(r"(?i)skills?[:\-]?\s*(?:\n)?(.+?)(?=\n\s*\n|\n[A-Z]{2,}|$)", resume_text, re.S)
        if skills_match:
            skills_text = skills_match.group(1).strip()
            # Try to preserve category format if present
            if ":" in skills_text:
                # already categorized
                data["skills"] = skills_text
            else:
                # convert to simple format
                skills_list = [s.strip("•- ") for s in re.split(r",|\n|•|-", skills_text) if s.strip()]
                data["skills"] = ", ".join(skills_list)

        # experience
        exp_match = re.search(r"(?i)experience[:\-]?\s*(?:\n)?(.+?)(?=\n\s*\n|\n[A-Z]{2,}|$)", resume_text, re.S)
        if exp_match:
            data["experience"] = exp_match.group(1).strip()

        # education
        edu_match = re.search(r"(?i)education[:\-]?\s*(?:\n)?(.+?)(?=\n\s*\n|\n[A-Z]{2,}|$)", resume_text, re.S)
        if edu_match:
            data["education"] = edu_match.group(1).strip()

    # Ensure returning simple strings so Streamlit text_area shows them
    return {
        "name": str(data.get("name", "")),
        "email": str(data.get("email", "")),
        "phone": str(data.get("phone", "")),
        "skills": str(data.get("skills", "")),
        "experience": str(data.get("experience", "")),
        "education": str(data.get("education", ""))
    }
