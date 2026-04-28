import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import traceback

# Core Logic Imports
from src.preprocess import extract_text_from_pdf
from src.section_extractor import extract_sections
from src.skill_extractor import extract_skills_as_list, extract_skills_categorized
from src.ranker import rank_resumes
from src.autonomous_learner import learner
from src.analytics import analyze_gaps_platinum, get_verdict

# UI Assets & Styles
from src.ui_styles import get_custom_css, get_top_nav
from src.ui_components import render_neural_canvas, render_radial_score, render_skill_badges, render_interview_card

# ── PAGE CONFIGURATION ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Resume Intelligence AI | Platinum Edition",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(get_custom_css(), unsafe_allow_html=True)
st.markdown(get_top_nav(), unsafe_allow_html=True)
render_neural_canvas()

# ── SESSION STATE ─────────────────────────────────────────────────────────────

if 'results' not in st.session_state: st.session_state.results = None
if 'file_meta' not in st.session_state: st.session_state.file_meta = None

# ── SIDEBAR COMMAND CENTER ────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("<div style='text-align:center; padding: 2rem 0;'><img src='https://cdn-icons-png.flaticon.com/512/2936/2936630.png' width='85' style='filter: drop-shadow(0 0 20px rgba(99,102,241,0.8)); animation: pulse 3s infinite;'><h1 class='pulse-text' style='font-weight:800; color:white; margin-top:15px; letter-spacing:-0.03em; font-size:1.8rem;'>INTEL CORE</h1><p style='color:#6366f1; font-size:0.75rem; letter-spacing:0.3em; font-weight:700;'>v3.2 PLATINUM</p></div>", unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.7rem; font-weight:800; color:#6366f1; letter-spacing:0.15em; margin-bottom:1rem;">⚡ NEURAL CALIBRATION</p>', unsafe_allow_html=True)
    
    auto_learn = st.toggle("🤖 Autonomous Learning", value=True)
    
    if auto_learn:
        lw = learner.train_on_feedback()
        st.markdown(f"""
            <div style='font-size:0.7rem; color:#fff; line-height:1.6; background:linear-gradient(135deg, rgba(99,102,241,0.2), rgba(6,182,212,0.2)); padding:12px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
                <div style='color:#64748b; font-size:0.6rem; font-weight:800; margin-bottom:5px;'>LIVE AI WEIGHTS</div>
                SKILLS: {lw['skills']:.2f}<br>EXPERIENCE: {lw['experience']:.2f}<br>EDUCATION: {lw['education']:.2f}
            </div>
        """, unsafe_allow_html=True)
        w_skills, w_exp, w_edu = lw['skills'], lw['experience'], lw['education']
    else:
        w_skills = st.slider("Technical Fit", 0.0, 1.0, 0.60)
        w_exp = st.slider("Experience", 0.0, 1.0, 0.30)
        w_edu = st.slider("Education", 0.0, 1.0, 0.10)
    
    total_w = max(0.01, w_skills + w_exp + w_edu)
    norm_weights = {"skills": w_skills/total_w, "experience": w_exp/total_w, "education": w_edu/total_w}
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.7rem; font-weight:800; color:#06b6d4; letter-spacing:0.15em; margin-bottom:1rem;">🧬 SYSTEM ENGINE</p>', unsafe_allow_html=True)
    anonymize = st.toggle("Privacy Mode", value=False)
    auto_expand = st.toggle("Smart Expansion", value=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🔥 PURGE NEURAL BUFFERS", use_container_width=True):
        st.session_state.results = None; st.session_state.file_meta = None; st.rerun()
    
    st.markdown("<div style='margin-top:40px; font-size:0.65rem; color:#64748b; text-align:center; font-weight:700; letter-spacing:0.1em;'>POWERED BY RESUME INTELLIGENCE PLATINUM</div>", unsafe_allow_html=True)

# ── MAIN BODY ─────────────────────────────────────────────────────────────────

st.markdown('<h1 class="main-header">RESUME<br>INTELLIGENCE</h1>', unsafe_allow_html=True)
st.markdown("<p style='font-size:1.1rem; color:#94a3b8; margin-bottom:2.5rem; font-weight:500; animation: fadeIn 1s ease-out;'>Autonomous Talent Discovery & Neural Match Engine</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🎯 Target Role Specification")
    job_desc = st.text_area("Paste the job description or requirements here...", height=250, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📄 Talent Pool")
    uploaded_files = st.file_uploader("Upload PDF Resumes", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files: st.success(f"✓ {len(uploaded_files)} resumes synchronized")
    st.markdown('</div>', unsafe_allow_html=True)

if st.button("🚀 EXECUTE NEURAL DISCOVERY", use_container_width=True):
    if not job_desc or not uploaded_files: st.error("Protocol Error: Missing Input.")
    else:
        try:
            with st.spinner("⚡ Calibrating Semantic Coverage & Categorizing Entities..."):
                resumes_data, file_meta = [], []
                for file in uploaded_files:
                    text = extract_text_from_pdf(file)
                    if not text.strip(): continue
                    skills_sec, exp, edu, training = extract_sections(text)
                    skills_nlp = extract_skills_as_list(text)
                    combined_skills = f"{' '.join(skills_nlp)} | {exp or text} | {edu or text} | {training or text}"
                    resumes_data.append(combined_skills)
                    file_meta.append({"name": file.name, "raw": text, "training_sec": training, "skills_list": skills_nlp})
                st.session_state.results = rank_resumes(job_desc, resumes_data, weights=norm_weights)
                st.session_state.file_meta = file_meta
                st.balloons()
        except Exception as e:
            st.error(f"Engine Fault: {e}"); st.code(traceback.format_exc())

# ── DASHBOARD ───────────────────────────────────────────────────────────────

if st.session_state.results:
    st.markdown("---")
    rows = []
    for rank, (idx, score, breakdown) in enumerate(st.session_state.results):
        name = f"Candidate {rank+1}" if anonymize else st.session_state.file_meta[idx]["name"]
        rows.append({
            "Rank": rank + 1, "Name": name, "Score": score, 
            "Skills": breakdown.get("skills", 0), "Experience": breakdown.get("experience", 0), 
            "Education": breakdown.get("education", 0), "Raw": st.session_state.file_meta[idx]["raw"],
            "SkillsList": st.session_state.file_meta[idx].get("skills_list", [])
        })
    df = pd.DataFrame(rows)

    st.header("🏆 Talent Intelligence Hub")
    tabs = st.tabs(["💎 Profiles", "📊 Visual Insights", "⚖️ Comparison", "🚩 Gap Analytics", "🎙️ Smart Interviewer", "📄 Raw Text"])
    tab_profiles, tab_visuals, tab_comparison, tab_gaps, tab_interviewer, tab_raw = tabs

    with tab_profiles:
        for i, row in df.iterrows():
            verdict, v_class = get_verdict(row['Score'])
            with st.expander(f"#{row['Rank']} {row['Name']} (Score: {row['Score']:.4f})", expanded=(i==0 and auto_expand)):
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; margin-bottom:20px; align-items:center;">
                    <div><span class="verdict-tag {v_class}">{verdict}</span></div>
                    {render_radial_score(row['Score'])}
                </div>
                <div style="display:grid; grid-template-columns: 1fr 2fr; gap:32px;">
                    <div><h5 style="color:#94a3b8; margin-bottom:16px;">Core Alignment</h5><div style="display:flex; flex-direction:column; gap:16px;">
                            <div><p style="font-size:0.75rem; color:#64748b; margin-bottom:4px;">Technical Fit Index</p><div style="height:4px; background:rgba(255,255,255,0.05);"><div style="height:100%; width:{row['Skills']*100}%; background:#6366f1;"></div></div></div>
                            <div><p style="font-size:0.75rem; color:#64748b; margin-bottom:4px;">Experience Relevance</p><div style="height:4px; background:rgba(255,255,255,0.05);"><div style="height:100%; width:{row['Experience']*100}%; background:#06b6d4;"></div></div></div>
                        </div></div>
                    <div><h5 style="color:#94a3b8; margin-bottom:16px;">Verified Technical DNA</h5>
                        {render_skill_badges(row['SkillsList'][:15], "matched")}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_visuals:
        v_col1, v_col2 = st.columns([1.2, 1])
        with v_col1:
            fig_score = px.bar(df.sort_values("Score", ascending=True), x="Score", y="Name", orientation='h', title="Talent Match Leaderboard", color="Score", color_continuous_scale="Tealgrn", template="plotly_dark", height=450)
            fig_score.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=60, b=20), font=dict(family="Plus Jakarta Sans"))
            st.plotly_chart(fig_score, use_container_width=True)
        with v_col2:
            st.markdown("<p style='font-size:1.1rem; font-weight:700; margin-bottom:1rem;'>🧬 Dimensional DNA Comparison (Top 3)</p>", unsafe_allow_html=True)
            top_df = df.head(min(3, len(df)))
            fig_radar = go.Figure()
            categories, colors = ['Skills', 'Experience', 'Education'], ['#6366f1', '#06b6d4', '#8b5cf6']
            for i, (idx, r) in enumerate(top_df.iterrows()):
                fig_radar.add_trace(go.Scatterpolar(r=[r['Skills'], r['Experience'], r['Education']], theta=categories, fill='toself', name=r['Name'], line=dict(color=colors[i % len(colors)])))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.1)"), angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"), bgcolor="rgba(0,0,0,0)"), showlegend=True, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=40, t=40, b=40), height=400)
            st.plotly_chart(fig_radar, use_container_width=True)

    with tab_comparison:
        if len(df) < 2: st.info("Upload at least 2 resumes to enable comparison mode.")
        else:
            c1, c2 = st.columns(2)
            cand1 = c1.selectbox("Select Candidate A", df["Name"].tolist(), index=0)
            cand2 = c2.selectbox("Select Candidate B", df["Name"].tolist(), index=1 if len(df) > 1 else 0)
            if cand1 and cand2:
                r1, r2 = df[df["Name"] == cand1].iloc[0], df[df["Name"] == cand2].iloc[0]
                cc1, cc2 = st.columns(2)
                for r, c in [(r1, cc1), (r2, cc2)]:
                    with c:
                        st.markdown(f'<div class="glass-card" style="padding:20px;"><h4 style="color:#6366f1;">{r["Name"]}</h4><p style="font-size:1.5rem; font-weight:800;">{r["Score"]:.4f}</p><hr style="opacity:0.1"><p><b>Skills:</b> {r["Skills"]:.2f}</p><p><b>Experience:</b> {r["Experience"]:.2f}</p><p><b>Education:</b> {r["Education"]:.2f}</p></div>', unsafe_allow_html=True)
                        analysis = analyze_gaps_platinum(job_desc, r["Raw"])
                        st.write("**Top Matches:**")
                        st.markdown(render_skill_badges(analysis["matched_hard"][:8], "matched"), unsafe_allow_html=True)

    with tab_gaps:
        for _, row in df.iterrows():
            analysis = analyze_gaps_platinum(job_desc, row["Raw"])
            with st.expander(f"Gap Analysis: {row['Name']}"):
                col_m, col_g = st.columns(2)
                with col_m:
                    st.markdown("##### ✅ Matched Skill Entities")
                    st.markdown(render_skill_badges(analysis["matched_hard"], "matched"), unsafe_allow_html=True)
                    if analysis["matched_soft"]:
                        st.markdown("<p style='font-size:0.7rem; color:#64748b; margin-top:10px;'>SOFT SKILLS MATCHED</p>", unsafe_allow_html=True)
                        st.markdown(render_skill_badges(analysis["matched_soft"], "soft"), unsafe_allow_html=True)
                with col_g:
                    st.markdown("##### 🚩 Analysis Gaps")
                    if analysis["critical_gaps"]:
                        st.markdown("<p style='font-size:0.7rem; color:#ef4444; font-weight:700;'>CRITICAL GAPS</p>", unsafe_allow_html=True)
                        st.markdown(render_skill_badges(analysis["critical_gaps"], "critical"), unsafe_allow_html=True)
                    if analysis["partial_matches"]:
                        st.markdown("<p style='font-size:0.7rem; color:#f59e0b; font-weight:700; margin-top:15px;'>PARTIAL MATCHES</p>", unsafe_allow_html=True)
                        st.markdown(render_skill_badges([item["gap"] for item in analysis["partial_matches"]], "partial"), unsafe_allow_html=True)

    with tab_interviewer:
        for i, row in df.iterrows():
            analysis = analyze_gaps_platinum(job_desc, row["Raw"])
            with st.expander(f"Strategic Protocol: {row['Name']}"):
                st.markdown("### 🧬 Phase 1: Technical DNA Validation")
                q1, q2 = st.columns(2)
                with q1:
                    if analysis["critical_gaps"]: st.markdown(render_interview_card("CRITICAL", f"The role requires mastery of {analysis['critical_gaps'][0].upper()}. How have you handled transitions into new tech stacks?", "Ability to map concepts, self-learning speed.", "Generic answers."), unsafe_allow_html=True)
                    else: st.markdown(render_interview_card("DEPTH", "You have a strong technical match. Can you describe the most difficult edge case you solved?", "Deep architectural understanding."), unsafe_allow_html=True)
                with q2:
                    if analysis["partial_matches"]: st.markdown(render_interview_card("SEMANTIC", f"We see your expertise in {analysis['partial_matches'][0]['covered_by'].upper()}. How would you translate those principles to our requirement for {analysis['partial_matches'][0]['gap'].upper()}?", "Conceptual agility."), unsafe_allow_html=True)
                st.markdown("### 🎭 Phase 2: Situational Intelligence")
                scenario = "scaling a high-traffic system" if "scale" in job_desc.lower() else "debugging a critical production issue"
                st.markdown(render_interview_card("SCENARIO", f"Scenario: You are tasked with {scenario}. Walk us through your thought process.", "Systems thinking, awareness of trade-offs."), unsafe_allow_html=True)
                st.markdown("### 📝 Scorecard")
                s1, s2, s3 = st.columns(3)
                s1.select_slider(f"Technical: {row['Name']}", ["Low", "Med", "High", "Expert"], key=f"s1_{row['Name']}_{i}")
                s2.select_slider(f"Comm: {row['Name']}", ["Low", "Med", "High", "Expert"], key=f"s2_{row['Name']}_{i}")
                s3.select_slider(f"Fit: {row['Name']}", ["Low", "Med", "High", "Expert"], key=f"s3_{row['Name']}_{i}")

    with tab_raw:
        for _, row in df.iterrows():
            with st.expander(f"Node Preview: {row['Name']}"): st.text_area("Content", row["Raw"], height=300, disabled=True, key=f"pv_{row['Name']}")

st.markdown("<center style='color:#64748b; font-size:0.8rem; margin-top:60px;'>RESUME INTELLIGENCE v3.2.0 • ENTITY-DRIVEN TALENT DISCOVERY • PLATINUM EDITION</center>", unsafe_allow_html=True)