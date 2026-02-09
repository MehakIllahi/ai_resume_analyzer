import streamlit as st
import re

from utils.pdf_utils import extract_pdf_text
from utils.similarity_utils import calculate_similarity
from utils.score_utils import extract_average_score
from utils.llm_utils import analyze_resume, generate_resume, extract_resume_fields
from utils.resume_pdf import generate_resume_pdf


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Resume Assistant",
    layout="wide"
)

# ================= PAGE ROUTING =================
page = st.query_params.get("page", "analyzer")


# ================= GLOBAL STYLES =================
st.markdown("""
<style>
.main { background-color: #F4F6FA; padding: 2rem; }
section[data-testid="stSidebar"] { background-color: #0F172A; }
.sidebar-title { color: #F8FAFC; font-size: 1.4rem; font-weight: 700; margin-bottom: 1rem; }
.nav-link { display: block; padding: 0.75rem 1rem; margin-bottom: 0.4rem;
    border-radius: 10px; color: #CBD5E1; font-size: 0.95rem; text-decoration: none; }
.nav-link:hover { background-color: #1E293B; color: #FFFFFF; }
.nav-active { background-color: #1E293B; color: #FFFFFF; position: relative; }
.nav-active::before { content: ""; position: absolute; left: 0; top: 18%;
    height: 64%; width: 4px; background-color: #4F46E5; }
.card { background: #FFFFFF; padding: 1.8rem; border-radius: 16px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.08); margin-bottom: 1.6rem; }
.stButton > button { background-color: #0F172A; color: #FFFFFF;
    border-radius: 10px; padding: 0.6rem 1.2rem; font-weight: 600; }
.metric { background: linear-gradient(135deg, #4F46E5, #6366F1);
    color: white; padding: 1.6rem; border-radius: 16px; text-align: center; }
</style>
""", unsafe_allow_html=True)


# ================= SIDEBAR =================
with st.sidebar:
    st.markdown('<div class="sidebar-title">🤖 AI Resume Assistant</div>', unsafe_allow_html=True)
    st.caption("Smart ATS Resume Platform")
    st.markdown("---")

    def nav(label, target):
        active = "nav-active" if page == target else ""
        st.markdown(
            f'<a href="?page={target}" class="nav-link {active}">{label}</a>',
            unsafe_allow_html=True
        )

    nav("📊 Resume Analyzer", "analyzer")
    nav("🧱 Resume Generator", "generator")


# ================= ANALYZER PAGE =================
if page == "analyzer":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Resume Analyzer")

    resume_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    jd = st.text_area("Paste Job Description", height=260)
    analyze = st.button("🚀 Analyze Resume")

    st.markdown('</div>', unsafe_allow_html=True)

    if analyze and resume_file and jd:
        resume_text = extract_pdf_text(resume_file)
        ats = calculate_similarity(resume_text, jd)
        report = analyze_resume(resume_text, jd)
        avg = extract_average_score(report)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='metric'><p>ATS</p><h1>{round(ats,3)}</h1></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric'><p>Score</p><h1>{round(avg,2)}/5</h1></div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📄 AI Analysis")
        st.markdown(report)
        st.markdown('</div>', unsafe_allow_html=True)


# ================= GENERATOR PAGE =================
if page == "generator":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧱 Resume Builder")

    raw_text = st.text_area("Paste Resume / LinkedIn / Profile Text", height=220)
    auto_fill = st.button("✨ Auto-Fill Resume Fields")
    st.markdown('</div>', unsafe_allow_html=True)

    # Defaults
    for key in ["name","email","phone","skills","education","experience","projects"]:
        st.session_state.setdefault(key, "")

    if auto_fill:
        data = extract_resume_fields(raw_text)
        for k in st.session_state.keys():
            if k in data:
                st.session_state[k] = data[k]
        st.success("Auto-filled successfully ✅")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    with st.form("resume_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", st.session_state.name)
            email = st.text_input("Email", st.session_state.email)
        with col2:
            phone = st.text_input("Phone", st.session_state.phone)

        skills = st.text_area("Skills", st.session_state.skills, height=120)
        education = st.text_area("Education", st.session_state.education, height=120)
        experience = st.text_area("Experience", st.session_state.experience, height=180)

        # ✅ OPTIONAL PROJECTS (UI UNCHANGED)
        projects = st.text_area("Projects (Optional)", st.session_state.projects, height=160)

        submitted = st.form_submit_button("✅ Generate Resume PDF")

    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        resume_text = generate_resume(
            name, email, phone, "",
            skills, experience, education, projects
        )

        generate_resume_pdf("resume.pdf", resume_text)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📄 Resume Preview")
        st.text(resume_text)

        with open("resume.pdf", "rb") as f:
            st.download_button("⬇️ Download Resume PDF", f, "resume.pdf")

        st.markdown('</div>', unsafe_allow_html=True)
