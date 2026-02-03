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
Create a PROFESSIONAL ATS FRIENDLY RESUME.

FORMAT EXACTLY:

NAME (ALL CAPS)
{role}
{email} | {phone}

SUMMARY
2-3 lines professional summary.

SKILLS
• {skills}

EXPERIENCE
{experience}

EDUCATION
{education}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a professional resume writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content


def extract_resume_fields(resume_text):
    prompt = f"""
Extract the following fields from the resume text and return ONLY valid JSON with keys: name, email, phone, skills, experience, education.

- `name`: string
- `email`: string
- `phone`: string
- `skills`: string (comma or newline separated)
- `experience`: string (can be multiple lines)
- `education`: string

Resume:
{resume_text}

Return only JSON.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a JSON extractor. Output only JSON."},
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
