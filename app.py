import streamlit as st
import sys
import os


# Fix path to import from src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from ranker import rank_resumes
from pdf_reader import extract_text_from_pdf

st.title("📄 Smart Resume Ranker")

# Job description input
job_desc = st.text_area("Enter Job Description")

# Upload multiple resumes
uploaded_files = st.file_uploader(
    "Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Rank Resumes"):

    if not job_desc or not uploaded_files:
        st.warning("Please provide job description and upload resumes")
    else:
        resumes = []

        for file in uploaded_files:
            text = extract_text_from_pdf(file)

            # simple fallback structure
            from section_extractor import extract_sections
            from skill_extractor import extract_skills


            skills_section, experience, education = extract_sections(text)

            # NLP skill extraction (stronger)
            skills_nlp = extract_skills(text)

            # Combine both (best of both worlds)
            skills = skills_section + " " + skills_nlp
            if not skills:
                skills = text
            if not experience:
                 experience = text
            if not education:
                education = text
               

            resumes.append(f"{skills} | {experience} | {education}")

        results = rank_resumes(job_desc, resumes)

        st.subheader("🏆 Ranking Results")

        for i, score in results:
            st.write(f"Resume {i+1} → Score: {score:.4f}")