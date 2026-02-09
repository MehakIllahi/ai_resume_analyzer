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


# ================= GENERATE RESUME =================
# def generate_resume(name, email, phone, role, skills, experience, education, projects=""):
    experience = experience.strip()
    is_fresher = experience == ""

    prompt = f"""
Create a PROFESSIONAL ATS FRIENDLY RESUME in plain text.

STRICT RULES:
- NO markdown
- NO **
- Use • bullets ONLY in EXPERIENCE and PROJECTS
- EXPERIENCE: exactly 4–5 bullets PER COMPANY
- EDUCATION: ONE LINE ONLY, NO bullets

FORMAT:

{name.upper()}
{email} | {phone}

{role}

SUMMARY
2-3 lines professional summary.

SKILLS
Frontend: ...
Backend: ...
Other: ...
"""

    # ================= EXPERIENCE =================
    if not is_fresher:
        prompt += f"""
EXPERIENCE

Company Name | Role | Timeline
• Responsibility or achievement
• Responsibility or achievement
• Responsibility or achievement
• Responsibility or achievement

RULES:
- Internship counts as experience
- Company line must NOT be a bullet
- Bullets ONLY under company
- DO NOT invent experience

INPUT EXPERIENCE TEXT:
{experience}
"""

    # ================= PROJECTS =================
    if projects.strip():
        prompt += f"""
PROJECTS

PROJECT NAME | TIMELINE
• What you built
• Tech stack
• Outcome

RULES FOR PROJECTS:
- Project name + timeline MUST be in UPPERCASE
- NO bullets on project title line
- Bullets ONLY for descriptions

INPUT PROJECT TEXT:
{projects}
"""

    # ================= EDUCATION =================
    prompt += f"""
EDUCATION
Degree | University | Timeline

INPUT EDUCATION TEXT:
{education}

IMPORTANT:
- NEVER add EXPERIENCE section for freshers
- NEVER add bullets under EDUCATION
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an ATS resume writer. "
                    "Strictly follow fresher vs experienced rules. "
                    "Plain text only."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    resume_text = response.choices[0].message.content

    # Cleanup
    resume_text = resume_text.replace("**", "")
    resume_text = re.sub(r"(EDUCATION[\s\S]*?)(\n\s*•.*)+", r"\1", resume_text)

    return resume_text


# ================= SORT EXPERIENCE =================
def extract_end_year(block):
    match = re.search(r"\|\s*\d{4}\s*[-–]\s*(\d{4}|Present|present)", block)
    if not match:
        return 0
    return 9999 if "present" in match.group(1).lower() else int(match.group(1))


# ================= EXTRACT RESUME FIELDS =================
def extract_resume_fields(resume_text):
    """
    Extracts resume fields from AI-generated resume.
    Internships are always included in experience.
    Skills are reliably extracted.
    """

    prompt = f"""
Extract resume fields from the following resume and return ONLY valid JSON.

IMPORTANT:
- EXPERIENCE must include full block:
  Company | Role | Timeline
  followed by • bullets
- Internship IS experience
- If no internship or job → experience = ""
- Preserve bullets EXACTLY using •
- Return skills exactly as in the resume

JSON FORMAT:
{{
  "name": "",
  "email": "",
  "phone": "",
  "frontend": "",
  "skills": "",
  "experience": "",
  "projects": "",
  "education": ""
}}

Resume:
{resume_text}

Return ONLY JSON. Do not add extra text.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Strict JSON extractor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw = re.sub(r"```json|```", "", response.choices[0].message.content).strip()

    # Attempt to parse JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # fallback: extract skills manually
        data = {}
        frontend_match = re.search(r"Frontend:\s*(.+)", resume_text)
        backend_match = re.search(r"Backend:\s*(.+)", resume_text)
        other_match = re.search(r"Other:\s*(.+)", resume_text)
        skills_list = []
        if frontend_match: skills_list.append(frontend_match.group(1).strip())
        if backend_match: skills_list.append(backend_match.group(1).strip())
        if other_match: skills_list.append(other_match.group(1).strip())
        data["skills"] = ", ".join(skills_list)
        # Experience extraction
        exp_match = re.search(r"(EXPERIENCE[\s\S]*?)\n\n(?:PROJECTS|EDUCATION)", resume_text)
        data["experience"] = exp_match.group(1).replace("EXPERIENCE\n", "").strip() if exp_match else ""

    def safe(key):
        val = data.get(key, "")
        return val.strip() if isinstance(val, str) else ""

# ---------- SORT EXPERIENCE (LATEST FIRST) ----------
    experience = safe("experience")
    if experience:
        # Split by company/internship blocks
        blocks = re.split(r"\n(?=[A-Z].+?\|.+?\|)", experience)
        cleaned_blocks = []

        for block in blocks:
            block = block.strip()
            # Only include blocks with bullets (experience) or valid company line
            if "•" in block:
                cleaned_blocks.append(block)
            elif "Internship" in block and block not in cleaned_blocks:
                cleaned_blocks.append(block)

        # Sort blocks by end year
        cleaned_blocks.sort(key=extract_end_year, reverse=True)
        experience = "\n\n".join(cleaned_blocks)


    # ---------- FRESHER HARD CHECK ----------
    if not experience.strip():
        experience = ""

    return {
        "name": safe("name"),
        "email": safe("email"),
        "phone": safe("phone"),
        "frontend": safe("frontend"),
        "skills": safe("skills"),
        "experience": experience,
        "projects": safe("projects"),
        "education": safe("education")
    }

def generate_resume(name, email, phone, role, skills, experience, education, projects=""):
    """
    Generates ATS-friendly resume in plain text.
    EXPERIENCE section is included only if there is real work experience (not internships).
    PROJECTS section is included only if there are projects.
    """
    experience = experience.strip()
    projects = projects.strip()
    is_fresher = experience == ""  # True if no real work experience

    # Handle skills: works for both dict and string
    if isinstance(skills, str):
        frontend_skills = backend_skills = other_skills = skills
    else:
        frontend_skills = skills.get("frontend", "")
        backend_skills = skills.get("backend", "")
        other_skills = skills.get("other", "")

    # ================= BASE PROMPT =================
    prompt = f"""
Create a PROFESSIONAL ATS FRIENDLY RESUME in plain text.

STRICT RULES:
- NO markdown
- NO **
- Use • bullets ONLY in EXPERIENCE and PROJECTS
- EDUCATION: ONE LINE ONLY, NO bullets

FORMAT:

{name.upper()}
{email} | {phone}

{role}

SUMMARY
2-3 lines professional summary.

SKILLS
Frontend: {frontend_skills}
Backend: {backend_skills}
Other: {other_skills}
"""

    # ================= EXPERIENCE =================
    if not is_fresher:
        # Only include EXPERIENCE if there is real work experience
        prompt += f"""
EXPERIENCE

Include all real jobs exactly as provided (internships will be ignored here).
For each company, provide 4 bullets describing responsibilities or achievements.

INPUT EXPERIENCE TEXT:
{experience}
"""

    # ================= PROJECTS =================
    if projects:
        prompt += f"""
PROJECTS

PROJECT NAME | TIMELINE
• What you built
• Tech stack
• Outcome

INPUT PROJECT TEXT:
{projects}
"""

    # ================= EDUCATION =================
    prompt += f"""
EDUCATION
Degree | University | Timeline

INPUT EDUCATION TEXT:
{education}

IMPORTANT:
- Do not invent EXPERIENCE for freshers
- Only include PROJECTS if provided
- Never add bullets under EDUCATION
"""

    # ================= CALL AI =================
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an ATS resume writer. "
                    "Only include EXPERIENCE section if there is real work experience, "
                    "do not include internships as EXPERIENCE. "
                    "Include PROJECTS only if provided. "
                    "Generate plain text resume only."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    resume_text = response.choices[0].message.content

    # Cleanup
    resume_text = resume_text.replace("**", "")
    resume_text = re.sub(r"(EDUCATION[\s\S]*?)(\n\s*•.*)+", r"\1", resume_text)

    return resume_text
