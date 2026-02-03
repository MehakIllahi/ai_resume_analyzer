import streamlit as st
import re

from utils.pdf_utils import extract_pdf_text
from utils.similarity_utils import calculate_similarity
from utils.score_utils import extract_average_score
from utils.llm_utils import analyze_resume, generate_resume, extract_resume_fields
from utils.resume_pdf import generate_resume_pdf

st.set_page_config("AI Resume Assistant", layout="wide")
st.title("🤖 AI Resume Assistant")


def clean_preview_text(text):
    if not text:
        return text
    text = text.replace("**", "")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.lower().startswith(("note", "disclaimer")):
            return "\n".join(lines[:i]).strip()
    return text


tab1, tab2 = st.tabs(["📊 Resume Analyzer", "🧱 Resume Generator"])


# ================= ANALYZER =================
with tab1:
    resume_file = st.file_uploader("Upload Resume PDF", type="pdf")
    jd = st.text_area("Job Description")

    if st.button("Analyze Resume"):
        if resume_file and jd:
            resume_text = extract_pdf_text(resume_file)
            ats = calculate_similarity(resume_text, jd)
            report = analyze_resume(resume_text, jd)
            avg = extract_average_score(report)

            st.metric("ATS Similarity", round(ats, 3))
            st.metric("AI Avg Score", round(avg, 2))
            st.markdown(report)
        else:
            st.warning("Please upload resume and job description")


# ================= GENERATOR =================
with tab2:
    st.subheader("📥 Paste Resume / Profile")

    raw_text = st.text_area("Paste resume content", height=250)

    if st.button("✨ Auto-fill from text"):
        data = extract_resume_fields(raw_text)

        st.session_state.name = data.get("name", "")
        st.session_state.email = data.get("email", "")
        st.session_state.phone = data.get("phone", "")
        st.session_state.skills = data.get("skills", "")
        st.session_state.education = data.get("education", "")
        st.session_state.experience = data.get("experience", "")

        st.success("Auto-filled successfully")
        st.rerun()

    # Defaults
    st.session_state.setdefault("name", "")
    st.session_state.setdefault("email", "")
    st.session_state.setdefault("phone", "")
    st.session_state.setdefault("skills", "")
    st.session_state.setdefault("education", "")
    st.session_state.setdefault("experience", "")

    with st.form("resume_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", st.session_state.name)
            email = st.text_input("Email", st.session_state.email)
        with col2:
            phone = st.text_input("Phone", st.session_state.phone)

        st.markdown("### 📌 Skills")
        skills = st.text_area(
            "Skills (comma or bullet separated)",
            value=st.session_state.skills,
            height=120
        )

        st.markdown("### 🎓 Education")
        education = st.text_area(
            "Education",
            value=st.session_state.education,
            height=120
        )

        st.markdown("### 💼 Experience")
        experience = st.text_area(
            "Experience",
            value=st.session_state.experience,
            height=180
        )

        submitted = st.form_submit_button("✅ Generate Resume PDF")

    if submitted:
        if not email.strip():
            st.error("❌ Email is required")
        elif not phone.strip():
            st.error("❌ Phone number is required")
        else:
            resume_text = generate_resume(
                name=name,
                email=email,
                phone=phone,
                role="",
                skills=skills,
                experience=experience,
                education=education
            )

            cleaned_resume = clean_preview_text(resume_text)
            generate_resume_pdf("resume.pdf", cleaned_resume)

            st.subheader("📄 Preview")
            st.text(cleaned_resume)

            with open("resume.pdf", "rb") as f:
                st.download_button("⬇️ Download Resume PDF", f, "resume.pdf")
