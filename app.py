import streamlit as st
from utils.pdf_utils import extract_pdf_text
from utils.similarity_utils import calculate_similarity
from utils.score_utils import extract_average_score
from utils.llm_utils import analyze_resume, generate_resume
from utils.resume_pdf import generate_resume_pdf


st.set_page_config(page_title="AI Resume Assistant", layout="wide")

st.title(" AI Resume Assistant")

# Initialize session state for caching analysis results
if "last_analysis_cache" not in st.session_state:
    st.session_state.last_analysis_cache = {}

tab1, tab2 = st.tabs(["📊 Resume Analyzer", "🧱 Resume Generator"])

# ---------------- ANALYZER ----------------
with tab1:
    with st.form("analyze_form"):
        resume_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
        jd = st.text_area("Job Description", placeholder="Paste the job description here...")
        submitted = st.form_submit_button("Analyze")

    if submitted:
        if not (resume_file and jd):
            st.warning("Please upload a resume PDF and provide the job description.")
        else:
            with st.spinner("Extracting resume and generating analysis..."):
                resume_text = extract_pdf_text(resume_file)
                
                # Create a simple cache key from first 100 chars of resume and JD
                cache_key = f"{hash(resume_text[:100])}-{hash(jd[:100])}"
                
                # Check if we have cached results
                if cache_key in st.session_state.last_analysis_cache:
                    cached = st.session_state.last_analysis_cache[cache_key]
                    ats = cached["ats"]
                    report = cached["report"]
                    avg = cached["avg"]
                    st.info("📌 Using cached analysis (from previous run)")
                else:
                    ats = calculate_similarity(resume_text, jd)
                    report = analyze_resume(resume_text, jd)
                    avg = extract_average_score(report)
                    
                    # Cache the results
                    st.session_state.last_analysis_cache[cache_key] = {
                        "ats": ats,
                        "report": report,
                        "avg": avg
                    }

            col1, col2 = st.columns(2)
            with col1:
                st.write("Few ATS use this score to shortlist candidates — Similarity Score:")
                st.subheader(f"{round(ats, 3)}")
            with col2:
                st.write("Total Average score according to our AI report:")
                st.subheader(f"{round(avg, 3)}")

            st.success("Scores generated successfully!")

            st.subheader("AI Generated Analysis Report:")
            st.markdown(
                f"""
                <div style='text-align: left; background-color: #0b0b0b; color: #e6e6e6; padding: 16px; border-radius: 8px; margin: 8px 0;'>
                    {report}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.download_button(
                label="Download Report",
                data=report,
                file_name="resume_report.txt",
                mime="text/plain",
            )

# ---------------- GENERATOR ----------------
with tab2:
    with st.form("generate_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone")
        role = st.text_input("Target Role")
        skills = st.text_area("Skills (comma separated or bullets)")
        experience = st.text_area("Experience (brief)")
        education = st.text_area("Education")
        gen_submitted = st.form_submit_button("Generate Resume PDF")

    if gen_submitted:
        if not (name and role):
            st.warning("Name and Target Role are required to generate a resume.")
        else:
            with st.spinner("Generating resume..."):
                resume_text = generate_resume(name, email, phone, role, skills, experience, education)
                pdf_path = "generated_resume.pdf"
                generate_resume_pdf(pdf_path, resume_text)

            st.subheader("Preview (Text)")
            st.text(resume_text)

            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download Resume PDF", f, file_name="resume.pdf")
