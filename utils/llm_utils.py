from groq import Groq

def get_report(resume, job_desc, api_key):
    client = Groq(api_key=api_key)
    prompt = f"""
    # Context:
    You are an AI Resume Analyzer. Analyze the resume based on the job description.

    Candidate Resume: {resume}
    Job Description: {job_desc}

    Instructions:
    - Score each point out of 5
    - Use ✅ ❌ ⚠️ for alignment
    - Provide suggestions at the end
    """
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )
    return completion.choices[0].message.content
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"   # WORKING MODEL

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def analyze_resume(resume, jd):
    prompt = f"""
You are an AI Resume Analyzer.

Analyze the candidate's resume against the job description.

Instructions:
- Score each relevant point out of 5.
- Use ✅ for strong match, ⚠️ for partial match, ❌ for mismatch.
- Provide **specific suggestions to improve the resume at the end**.
- Make the output easy to read.

Resume:
{resume}

Job Description:
{jd}

End your response with:

"SUGGESTIONS TO IMPROVE YOUR RESUME:"
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content


def generate_resume(name, email, phone, role, skills, experience, education):
    prompt = f"""
Create a PROFESSIONAL ATS-FRIENDLY RESUME.

FORMAT EXACTLY LIKE THIS:

NAME (ALL CAPS)
Job Title
Email | Phone

SUMMARY
2-3 line professional summary.

SKILLS
• Bullet points

EXPERIENCE
Job Title – Company
• Achievement based bullet points

EDUCATION
Degree – University

DETAILS:
Name: {name}
Email: {email}
Phone: {phone}
Role: {role}
Skills: {skills}
Experience: {experience}
Education: {education}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content
# import os
# import time
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()

# # Configure Gemini
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# MODEL_NAME = "gemini-1.5-flash"
# model = genai.GenerativeModel(MODEL_NAME)


# # ---------- SAFE GENERATE (enhanced rate-limit handling) ----------
# def safe_generate(prompt, retries=10):
#     """
#     Generate content with exponential backoff for rate limiting.
#     Retries up to 10 times with increasing wait times.
#     """
#     for attempt in range(retries):
#         try:
#             response = model.generate_content(
#                 prompt,
#                 generation_config={
#                     "temperature": 0.3,
#                     "max_output_tokens": 500,  # Reduced from 1200
#                     "top_p": 0.8,
#                     "top_k": 20,
#                 }
#             )
#             if response.text:
#                 return response.text
#             else:
#                 return "⚠️ Empty response from API. Please try again."

#         except Exception as e:
#             error = str(e).lower()
            
#             # Handle rate limit errors (429, quota exceeded, etc.)
#             if "rate" in error or "429" in error or "quota" in error or "too many requests" in error:
#                 # Exponential backoff: 15s, 30s, 60s, 120s, etc.
#                 wait_time = 15 * (2 ** attempt)
                
#                 if attempt < retries - 1:
#                     print(f"⏳ Rate limited. Retrying in {wait_time}s... (Attempt {attempt + 1}/{retries})")
#                     time.sleep(wait_time)
#                 else:
#                     return "⚠️ Rate limit exceeded after multiple retries. Please wait 5+ minutes and try again."
#             else:
#                 # Non-rate-limit errors
#                 return f"❌ Error: {str(e)}"

#     return "⚠️ Failed to generate response. Please try again later."


# # ---------- ANALYZE RESUME ----------
# def analyze_resume(resume, jd):
#     """Analyze resume with minimal data sent to API"""
#     # Truncate to first 2000 chars to reduce payload
#     resume_short = resume[:2000] if len(resume) > 2000 else resume
#     jd_short = jd[:1500] if len(jd) > 1500 else jd
    
#     prompt = f"""You are an AI Resume Analyzer.

# Analyze the resume against the job description. Be concise.

# Resume (excerpt):
# {resume_short}

# Job Description (excerpt):
# {jd_short}

# Output:
# - Score each relevant skill/experience point out of 5
# - Use ✅ ❌ ⚠️ for alignment
# - Provide 3-4 bullet point suggestions to improve

# SUGGESTIONS TO IMPROVE YOUR RESUME:"""
#     return safe_generate(prompt)


# # ---------- GENERATE RESUME ----------
# def generate_resume(name, email, phone, role, skills, experience, education):
#     """Generate resume with compressed input"""
#     prompt = f"""Create a PROFESSIONAL ATS-FRIENDLY RESUME (concise format).

# NAME (ALL CAPS)
# Job Title
# Email | Phone

# SUMMARY
# 1-2 lines only.

# SKILLS
# • {skills[:200] if skills else "Not provided"}

# EXPERIENCE
# {experience[:400] if experience else "Not provided"}

# EDUCATION
# {education[:200] if education else "Not provided"}

# Create resume for: {name} | {role}"""
#     return safe_generate(prompt)
