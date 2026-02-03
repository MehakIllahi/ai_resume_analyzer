import streamlit as st
import json

from utils.pdf_utils import extract_pdf_text
from utils.similarity_utils import calculate_similarity
from utils.score_utils import extract_average_score
from utils.llm_utils import (
    analyze_resume,
    generate_resume,
    extract_resume_fields
)
from utils.resume_pdf import generate_resume_pdf


st.set_page_config("AI Resume Assistant", layout="wide")
st.title("🤖 AI Resume Assistant")

tab1, tab2 = st.tabs(["📊 Resume Analyzer", "🧱 Resume Generator"])


# ================= ANALYZER =================
with tab1:
    resume_file = st.file_uploader("Upload Resume PDF", type="pdf")
    jd = st.text_area("Job Description")

    if st.button("Analyze Resume"):
        if resume_file and jd:
            try:
                with st.spinner("Extracting resume..."):
                    resume_text = extract_pdf_text(resume_file)

                with st.spinner("Analyzing with AI..."):
                    ats = calculate_similarity(resume_text, jd)
                    report = analyze_resume(resume_text, jd)
                    avg = extract_average_score(report)

                st.metric("ATS Similarity Score", round(ats, 3))
                st.metric("AI Average Score", round(avg, 2))
                st.markdown(report)

            except ValueError as e:
                st.error(str(e))

        else:
            st.warning("Please upload resume and job description")


# ================= GENERATOR =================
with tab2:
    st.subheader("📥 Paste Resume / Profile Summary")

    raw_text = st.text_area(
        "Paste resume content",
        height=250
    )

    if st.button("✨ Auto-fill from text"):
        with st.spinner("Extracting..."):
            data = extract_resume_fields(raw_text)
            if isinstance(data, dict):
                st.session_state.update(data)
            else:
                st.error("Failed to extract resume data")

            st.success("Auto-filled successfully")

    # Initialize session state for dynamic fields
    if "skills_list" not in st.session_state:
        st.session_state.skills_list = [""]
    if "education_list" not in st.session_state:
        st.session_state.education_list = [""]
    if "experience_list" not in st.session_state:
        st.session_state.experience_list = [""]

    with st.form("resume_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", st.session_state.get("name", ""))
            email = st.text_input("Email", st.session_state.get("email", ""))
        with col2:
            phone = st.text_input("Phone", st.session_state.get("phone", ""))
            role = st.text_input("Target Role")

        # ===== SKILLS (Dynamic) =====
        st.markdown("### 📌 Skills")
        skills_list = st.session_state.skills_list
        for idx, skill in enumerate(skills_list):
            st.text_input(f"Skill {idx + 1}", value=skill, key=f"skill_{idx}")

        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            if st.form_submit_button("➕ Add Skill"):
                st.session_state.skills_list.append("")
                st.rerun()
        with col_s2:
            if len(skills_list) > 1 and st.form_submit_button("➖ Remove Last Skill"):
                st.session_state.skills_list.pop()
                st.rerun()

        st.divider()

        # ===== EDUCATION (Dynamic) =====
        st.markdown("### 🎓 Education")
        education_list = st.session_state.education_list
        for idx, edu in enumerate(education_list):
            st.text_area(f"Education {idx + 1}", value=edu, height=80, key=f"education_{idx}")

        col_e1, col_e2 = st.columns([1, 1])
        with col_e1:
            if st.form_submit_button("➕ Add Education"):
                st.session_state.education_list.append("")
                st.rerun()
        with col_e2:
            if len(education_list) > 1 and st.form_submit_button("➖ Remove Last Education"):
                st.session_state.education_list.pop()
                st.rerun()

        st.divider()

        # ===== EXPERIENCE (Dynamic) =====
        st.markdown("### 💼 Experience")
        experience_list = st.session_state.experience_list
        for idx, exp in enumerate(experience_list):
            st.text_area(f"Experience {idx + 1}", value=exp, height=80, key=f"experience_{idx}")

        col_ex1, col_ex2 = st.columns([1, 1])
        with col_ex1:
            if st.form_submit_button("➕ Add Experience"):
                st.session_state.experience_list.append("")
                st.rerun()
        with col_ex2:
            if len(experience_list) > 1 and st.form_submit_button("➖ Remove Last Experience"):
                st.session_state.experience_list.pop()
                st.rerun()

        st.divider()
        submitted = st.form_submit_button("✅ Generate Resume PDF")

    if submitted:
        # Collect all skills, education, and experience from form
        skills_collected = [st.session_state.get(f"skill_{i}", "") for i in range(len(st.session_state.skills_list))]
        education_collected = [st.session_state.get(f"education_{i}", "") for i in range(len(st.session_state.education_list))]
        experience_collected = [st.session_state.get(f"experience_{i}", "") for i in range(len(st.session_state.experience_list))]

        skills_str = ", ".join([s.strip() for s in skills_collected if s.strip()])
        education_str = "\n\n".join([e.strip() for e in education_collected if e.strip()])
        experience_str = "\n\n".join([e.strip() for e in experience_collected if e.strip()])

        resume_text = generate_resume(
            name, email, phone, role, skills_str, experience_str, education_str
        )

        generate_resume_pdf("resume.pdf", resume_text)

        st.subheader("Preview")
        st.text(resume_text)

        with open("resume.pdf", "rb") as f:
            st.download_button("📄 Download Resume PDF", f, "resume.pdf")
