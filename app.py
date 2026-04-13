import streamlit as st
import sys
import os
import pandas as pd
def get_matched_skills(job_desc, skills_text):
    job_words = set(job_desc.lower().split())
    skills = skills_text.lower().split()

    matched = [s for s in skills if s in job_words]
    return matched
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from ranker import rank_resumes
from pdf_reader import extract_text_from_pdf
from skill_extractor import extract_skills
from section_extractor import extract_sections

st.set_page_config(page_title="Smart Resume Ranker", layout="wide")

st.title("🚀 Smart Resume Ranker")

job_desc = st.text_area("📌 Enter Job Description")

uploaded_files = st.file_uploader(
    "📂 Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("🔥 Rank Resumes"):

    if not job_desc or not uploaded_files:
        st.warning("Please provide job description and upload resumes")
    else:
        resumes = []
        names = []
        skills_list = []

        for file in uploaded_files:
            text = extract_text_from_pdf(file)

            if not text.strip():
                st.warning(f"Could not read {file.name}")
                continue

            skills_sec, exp, edu = extract_sections(text)
            skills_nlp = extract_skills(text)

            skills = skills_sec + " " + skills_nlp

            if not skills:
                skills = text
            if not exp:
                exp = text
            if not edu:
                edu = text

            resumes.append(f"{skills} | {exp} | {edu}")
            names.append(file.name)
            skills_list.append(skills)

        results = rank_resumes(job_desc, resumes)

        if not results:
            st.warning("No valid resumes could be ranked")
            st.stop()

        st.subheader("🏆 Ranking Results")

        # Convert to DataFrame
        data = []
        for rank, (i, score) in enumerate(results):
            data.append({
                "Rank": rank + 1,
                "Name": names[i],
                "Score": round(score, 4),
                "Skills": skills_list[i]
            })

        df = pd.DataFrame(data)

        # 🌟 Highlight top candidate
        st.success(f"🥇 Top Candidate: {df.iloc[0]['Name']}")

        # 📊 Bar chart
        st.subheader("📊 Score Visualization")
        st.bar_chart(df.set_index("Name")["Score"])

        # 🎴 Cards UI
        st.subheader("📄 Resume Details")

        for _, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 3])

                with col1:
                    st.metric("Rank", row["Rank"])
                    st.progress(row["Score"])

                with col2:
                    st.markdown(f"### {row['Name']}")
                    st.markdown(f"**Score:** {row['Score']}")
                    st.markdown(f"**Skills Detected:** {row['Skills'][:200]}...")

                    matched = get_matched_skills(job_desc, row["Skills"])
                    st.markdown("**Matched Skills:**")
                    if matched:
                        badges = " ".join([
                            f"<span style='background-color:#28a745; color:white; padding:5px 10px; border-radius:10px; margin:2px;'>{m}</span>"
                            for m in matched
                        ])
                        st.markdown(badges, unsafe_allow_html=True)
                    else:
                        st.write("No strong match found")

                st.divider()