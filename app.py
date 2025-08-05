import streamlit as st
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer, util
from docx import Document
from nlp_utils import extract_keywords, match_keywords_fuzzy
from datetime import datetime
import os
import openai
from dotenv import load_dotenv

# --- Load environment variables from .env ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Streamlit Page Config ---
st.set_page_config(page_title="📄 Resume–Job Relevance Matcher", layout="centered")
st.title("📄 Resume–Job Relevance Matcher")

# --- File Upload & Job Description ---
uploaded_file = st.file_uploader("Upload your resume (PDF, TXT, or DOCX)", type=["pdf", "txt", "docx"])
job_description = st.text_area("Paste the job description here", height=200)

# --- Load Transformer Model Once ---
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# --- Universal Resume Text Extractor ---
def get_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == "pdf":
        return extract_text(uploaded_file)
    elif file_type == "txt":
        return uploaded_file.read().decode("utf-8")
    elif file_type == "docx":
        doc = Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

# --- Match Report Generator ---
def generate_match_report(filename, job_desc, matched_keywords, keyword_score, relevance_score):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""📄 Resume–Job Relevance Report
==============================
🕒 Generated on: {now}

📁 Resume File: {filename}
📝 Job Summary: {job_desc.strip().splitlines()[0][:100]}...

🔑 Matched Keywords: {', '.join(matched_keywords) if matched_keywords else 'None'}
📊 Keyword Match Score: {keyword_score:.2f}%
🤖 Semantic Relevance Score: {relevance_score:.2f}%

📌 Feedback:
"""
    if relevance_score >= 80:
        report += "✅ Excellent match! Your resume aligns very well with the job."
    elif relevance_score >= 50:
        report += "⚠️ Fair match. You might want to improve your resume wording."
    else:
        report += "❌ Low match. Consider tailoring your resume more closely to this role."

    return report

# --- OpenAI Resume Suggestions ---
def generate_resume_suggestions(missing_keywords):
    if not missing_keywords:
        return ["Your resume covers all important skills well!"]

    prompt = (
        "You are a professional resume writer. Given these key skills and phrases missing from "
        "a candidate's resume: "
        f"{', '.join(missing_keywords)}. Provide concise, impactful bullet points "
        "that the candidate can add to their resume to improve their relevance for the job."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        suggestions = response.choices[0].message.content.strip().split("\n")
        return [s.strip("-*• ") for s in suggestions if s.strip()]
    except Exception as e:
        return [f"Error generating suggestions: {e}"]

# --- Main Logic ---
if uploaded_file and job_description.strip():
    with st.spinner("Analyzing match..."):
        resume_text = get_text_from_file(uploaded_file)

        resume_keywords = extract_keywords(resume_text)
        job_keywords = extract_keywords(job_description)

        keyword_results = match_keywords_fuzzy(resume_keywords, job_keywords)

        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        job_embedding = model.encode(job_description, convert_to_tensor=True)
        similarity_score = util.cos_sim(resume_embedding, job_embedding).item()
        percentage_score = round(similarity_score * 100, 2)

        # --- Display Keywords ---
        with st.expander("🔍 Extracted Keywords"):
            st.markdown("**📄 Resume Keywords:**")
            st.markdown(", ".join(resume_keywords) or "_None_")
            st.markdown("**📝 Job Description Keywords:**")
            st.markdown(", ".join(job_keywords) or "_None_")

        # --- Keyword Match Score ---
        st.subheader("🔑 Keyword Match")
        st.metric(label="Keyword Match Score", value=f"{keyword_results['match_score']:.2f}%")

        st.markdown("**Matched Keywords:**")
        if keyword_results["matched_keywords"]:
            st.markdown(
                " ".join([
                    f"<span style='background-color:#d1e7dd;color:#0f5132;"
                    f"padding:4px 8px;margin:2px;border-radius:10px;"
                    f"display:inline-block;font-size:90%'>{kw}</span>"
                    for kw in keyword_results["matched_keywords"]
                ]),
                unsafe_allow_html=True
            )
        else:
            st.markdown("_No matched keywords found._")

        # --- Semantic Score ---
        st.subheader("🤖 Semantic Relevance")
        st.metric(label="Semantic Relevance Score", value=f"{percentage_score}%")

        if percentage_score >= 80:
            st.balloons()
            st.info("✅ Excellent match! Your resume aligns very well with the job.")
        elif percentage_score >= 50:
            st.warning("⚠️ Fair match. You might want to improve your resume wording.")
        else:
            st.error("❌ Low match. Consider tailoring your resume more closely to this role.")

        # --- Improvement Suggestions ---
        missing_keywords = set(job_keywords) - set(resume_keywords)

        if percentage_score < 80:
            st.subheader("💡 Resume Improvement Suggestions")
            if missing_keywords:
                st.write("Consider adding or emphasizing these keywords/skills to improve your match:")
                for kw in sorted(missing_keywords):
                    st.markdown(f"- **{kw}**")
            else:
                st.write("Your resume contains all key terms! Great job.")
        else:
            st.info("Your resume matches very well, no major suggestions needed.")

        # --- AI Resume Suggestions ---
        if percentage_score < 80 and missing_keywords:
            st.subheader("🤖 AI-Generated Resume Suggestions")
            suggestions = generate_resume_suggestions(missing_keywords)
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")

        # --- Downloadable Match Report ---
        report_text = generate_match_report(
            filename=uploaded_file.name,
            job_desc=job_description,
            matched_keywords=keyword_results["matched_keywords"],
            keyword_score=keyword_results["match_score"],
            relevance_score=percentage_score
        )

        st.download_button(
            label="📥 Download Match Report (.txt)",
            data=report_text,
            file_name="match_report.txt",
            mime="text/plain"
        )