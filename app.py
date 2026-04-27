import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import io
import traceback
from datetime import datetime

# ── Setup ───────────────────────────────────────────────────────────────────

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from ranker import rank_resumes, get_semantic_coverage
    from pdf_reader import extract_text_from_pdf
    from skill_extractor import extract_skills_categorized, extract_skills_as_list
    from section_extractor import extract_sections
    from training_recommender import get_recommendations
    from autonomous_learner import learner
    from preprocess import clean_text
except ImportError as e:
    st.error(f"Critical System Error: Missing modules. Details: {e}")
    st.stop()

st.set_page_config(
    page_title="Resume Intelligence AI v3.2",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom Styling (Platinum v3.2) ───────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --primary: #6366f1;
        --secondary: #06b6d4;
        --accent: #8b5cf6;
        --bg: #0f172a;
        --sidebar-bg: #0b0f1a;
        --card-bg: rgba(30, 41, 59, 0.7);
    }

    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: radial-gradient(circle at 30% 30%, #1e1b4b 0%, #0f172a 100%); color: #f8fafc; }

    /* Sidebar Ultra Polish */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b0f1a 0%, #0f172a 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    .glass-card {
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 28px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.5);
    }

    .main-header {
        font-size: 5rem;
        font-weight: 800;
        letter-spacing: -0.06em;
        background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 50%, #2dd4bf 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.0;
        margin-bottom: 10px;
    }

    /* Badges */
    .skill-badge {
        padding: 6px 14px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        margin: 5px;
        display: inline-block;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .matched-badge { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border-color: rgba(16, 185, 129, 0.3); }
    .gap-critical { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border-color: rgba(239, 68, 68, 0.4); }
    .gap-partial { background: rgba(245, 158, 11, 0.15); color: #fcd34d; border-color: rgba(245, 158, 11, 0.3); }
    .soft-badge { background: rgba(99, 102, 241, 0.1); color: #c7d2fe; border-color: rgba(99, 102, 241, 0.2); }

    .verdict-tag { padding: 4px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; }
    .verdict-high { background: #10b981; color: #fff; }
    .verdict-med { background: #f59e0b; color: #fff; }
    .verdict-low { background: #ef4444; color: #fff; }

    /* Interview Cards */
    .interview-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 4px solid var(--primary);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .hint-box { font-size: 0.8rem; color: #10b981; margin-top: 10px; font-weight: 600; }
    .warning-box { font-size: 0.8rem; color: #ef4444; margin-top: 5px; font-weight: 600; }

    /* Hide Streamlit stuff */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────────────────────

if 'results' not in st.session_state: st.session_state.results = None
if 'file_meta' not in st.session_state: st.session_state.file_meta = None

# ── Sidebar UI ───────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("<div style='text-align:center; padding-bottom:1rem;'><img src='https://cdn-icons-png.flaticon.com/512/2936/2936630.png' width='60' style='filter: drop-shadow(0 0 10px rgba(99,102,241,0.5));'><h3 style='font-weight:800; color:white; margin-top:10px;'>INTEL HUB</h3></div>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown('<p style="font-size:0.7rem; font-weight:800; color:#64748b; letter-spacing:0.15em; margin-bottom:1rem;">NEURAL CALIBRATION</p>', unsafe_allow_html=True)
    
    auto_learn = st.toggle("🤖 Autonomous Learning Mode", value=True, help="When enabled, the system learns from your Hire/Reject decisions to automatically optimize weights.")
    
    if auto_learn:
        learned_weights = learner.train_on_feedback()
        st.info("System is using AI-optimized weights based on your historical behavior.")
        w_skills = learned_weights["skills"]
        w_exp = learned_weights["experience"]
        w_edu = learned_weights["education"]
        w_train = learned_weights["training"]
        
        # Display current learned weights (read-only)
        st.caption(f"Skills: {w_skills:.2f} | Exp: {w_exp:.2f} | Edu: {w_edu:.2f} | Train: {w_train:.2f}")
    else:
        w_skills = st.slider("Technical Skill Precision", 0.0, 1.0, 0.50)
        w_exp = st.slider("Experience Density", 0.0, 1.0, 0.25)
        w_edu = st.slider("Educational Alignment", 0.0, 1.0, 0.15)
        w_train = st.slider("Certification Intensity", 0.0, 1.0, 0.10)
    
    total_w = w_skills + w_exp + w_edu + w_train
    norm_weights = {
        "skills": w_skills/total_w, 
        "experience": w_exp/total_w, 
        "education": w_edu/total_w,
        "training": w_train/total_w
    }
    
    st.divider()
    st.markdown('<p style="font-size:0.7rem; font-weight:800; color:#64748b; letter-spacing:0.15em; margin-bottom:1rem;">SYSTEM PREFERENCES</p>', unsafe_allow_html=True)
    anonymize = st.toggle("Candidate Privacy Mode", value=False)
    auto_expand = st.toggle("Auto-Expand Analysis", value=True)
    
    st.divider()
    if st.button("🗑️ Reset Neural Buffers", use_container_width=True):
        st.session_state.results = None
        st.session_state.file_meta = None
        st.rerun()
    st.caption("Resume Intelligence v3.2.0 Platinum")

# ── Intelligence Helpers ────────────────────────────────────────────────────

def get_verdict(score):
    if score > 0.82: return ("Elite Selection", "verdict-high")
    if score > 0.68: return ("Strategic Potential", "verdict-med")
    return ("Low Alignment", "verdict-low")

def analyze_gaps_platinum(job_desc, resume_text):
    """
    Platinum Gap Analysis: Distinguishes between Hard/Soft skills and detects Semantic Coverage.
    """
    jd_cat = extract_skills_categorized(job_desc)
    res_cat = extract_skills_categorized(resume_text)
    
    # 1. Matches
    matched_hard = sorted(list(jd_cat["hard"] & res_cat["hard"]))
    matched_soft = sorted(list(jd_cat["soft"] & res_cat["soft"]))
    
    # 2. Potential Gaps (Hard Skills)
    jd_hard = jd_cat["hard"]
    res_hard = res_cat["hard"]
    potential_gaps = jd_hard - res_hard
    
    critical_gaps = []
    partial_matches = [] # Missing but semantically covered
    
    if potential_gaps:
        resume_all_skills = sorted(list(res_hard))
        for gap in potential_gaps:
            score, closest = get_semantic_coverage(gap, resume_all_skills)
            if score > 0.72:
                partial_matches.append({"gap": gap, "covered_by": closest, "confidence": score})
            else:
                critical_gaps.append(gap)
                
    return {
        "matched_hard": matched_hard,
        "matched_soft": matched_soft,
        "critical_gaps": sorted(critical_gaps),
        "partial_matches": sorted(partial_matches, key=lambda x: x['confidence'], reverse=True)
    }

# ── Main Application ─────────────────────────────────────────────────────────

st.markdown('<h1 class="main-header">Resume Intelligence</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748b; font-size:1.1rem; font-weight:600; margin-bottom:3.5rem; letter-spacing:0.1em; text-transform:uppercase;">Platinum Entity-Discovery & Semantic Coverage Engine</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="xlarge")
with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🎯 Job Specification")
    job_desc = st.text_area("Paste requirements...", height=280, placeholder="Senior Lead Architect...", label_visibility="collapsed")
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
                    file_meta.append({
                        "name": file.name, 
                        "raw": text, 
                        "training_sec": training,
                        "skills_list": skills_nlp
                    })
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
            "Rank": rank + 1, 
            "Name": name, 
            "Score": score, 
            "Skills": breakdown.get("skills", 0), 
            "Experience": breakdown.get("experience", 0), 
            "Education": breakdown.get("education", 0), 
            "Training": breakdown.get("training", 0),
            "Raw": st.session_state.file_meta[idx]["raw"],
            "TrainingSec": st.session_state.file_meta[idx].get("training_sec", ""),
            "SkillsList": st.session_state.file_meta[idx].get("skills_list", [])
        })
    df = pd.DataFrame(rows)

    st.header("🏆 Talent Intelligence Hub")
    tab_profiles, tab_visuals, tab_comparison, tab_gaps, tab_training, tab_interviewer, tab_raw = st.tabs([
        "💎 Profiles", "📊 Visual Insights", "⚖️ Comparison", "🚩 Gap Analytics", "🎓 Training & Growth", "🎙️ Smart Interviewer", "📄 Raw Text"
    ])



    with tab_profiles:
        for i, row in df.iterrows():
            verdict, v_class = get_verdict(row['Score'])
            with st.expander(f"#{row['Rank']} {row['Name']} (Score: {row['Score']:.4f})", expanded=(i==0 and auto_expand)):
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                    <div><span class="verdict-tag {v_class}">{verdict}</span><span style="color:#64748b; font-size:0.9rem; margin-left:12px;">Neural Match: {(row['Score']*100):.1f}%</span></div>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 2fr; gap:32px;">
                    <div><h5 style="color:#94a3b8; margin-bottom:16px;">Core Alignment</h5><div style="display:flex; flex-direction:column; gap:16px;">
                            <div><p style="font-size:0.75rem; color:#64748b; margin-bottom:4px;">Technical Fit Index</p><div style="height:4px; background:rgba(255,255,255,0.05);"><div style="height:100%; width:{row['Skills']*100}%; background:#6366f1;"></div></div></div>
                            <div><p style="font-size:0.75rem; color:#64748b; margin-bottom:4px;">Experience Relevance</p><div style="height:4px; background:rgba(255,255,255,0.05);"><div style="height:100%; width:{row['Experience']*100}%; background:#06b6d4;"></div></div></div>
                            <div><p style="font-size:0.75rem; color:#64748b; margin-bottom:4px;">Certification Intensity</p><div style="height:4px; background:rgba(255,255,255,0.05);"><div style="height:100%; width:{row['Training']*100}%; background:#8b5cf6;"></div></div></div>
                        </div></div>
                    <div><h5 style="color:#94a3b8; margin-bottom:16px;">Verified Technical DNA</h5>
                        {"".join([f'<span class="skill-badge matched-badge">{s}</span>' for s in row['SkillsList'][:15]])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_visuals:
        st.subheader("📊 Intelligence Visualization")
        
        v_col1, v_col2 = st.columns([1.2, 1])
        
        with v_col1:
            # 1. Leaderboard Match Score
            fig_score = px.bar(
                df.sort_values("Score", ascending=True),
                x="Score",
                y="Name",
                orientation='h',
                title="Talent Match Leaderboard",
                color="Score",
                color_continuous_scale="Tealgrn",
                template="plotly_dark",
                height=450
            )
            fig_score.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=60, b=20),
                font=dict(family="Plus Jakarta Sans")
            )
            st.plotly_chart(fig_score, use_container_width=True)

        with v_col2:
            # 2. Radar Chart for Top Candidates
            st.markdown("<p style='font-size:1.1rem; font-weight:700; margin-bottom:1rem;'>🧬 Dimensional DNA Comparison (Top 3)</p>", unsafe_allow_html=True)
            top_n = min(3, len(df))
            top_df = df.head(top_n)
            
            fig_radar = go.Figure()
            categories = ['Skills', 'Experience', 'Education', 'Training']
            
            colors = ['#6366f1', '#06b6d4', '#8b5cf6', '#ec4899']
            for i, (idx, row) in enumerate(top_df.iterrows()):
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row['Skills'], row['Experience'], row['Education'], row['Training']],
                    theta=categories,
                    fill='toself',
                    name=row['Name'],
                    line=dict(color=colors[i % len(colors)])
                ))
                
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(255,255,255,0.1)"),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                    bgcolor="rgba(0,0,0,0)"
                ),
                showlegend=True,
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=40, b=40),
                height=400
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        st.divider()
        
        # 3. Skill Frequency
        st.markdown("<h3 style='margin-bottom:1.5rem;'>🛠️ Talent Pool Skill Distribution</h3>", unsafe_allow_html=True)
        all_skills = []
        for _, row in df.iterrows():
            all_skills.extend(row['SkillsList'])
        
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts().head(12).reset_index()
            skill_counts.columns = ['Skill', 'Count']
            fig_skills = px.bar(
                skill_counts,
                x='Skill',
                y='Count',
                title="Top 12 Most Frequent Skills Found",
                color='Count',
                color_continuous_scale="Purp",
                template="plotly_dark",
                text_auto=True
            )
            fig_skills.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(title=""),
                yaxis=dict(title="Frequency"),
                font=dict(family="Plus Jakarta Sans")
            )
            st.plotly_chart(fig_skills, use_container_width=True)
        else:
            st.warning("No technical entities detected for aggregate analysis.")

        st.divider()
        st.markdown("### 🗺️ Skill Match Heatmap (Top 10 JD Requirements)")
        jd_skills = extract_skills_categorized(job_desc)["hard"]
        if jd_skills:
            top_jd_skills = sorted(list(jd_skills))[:10]
            heatmap_data = []
            for _, row in df.iterrows():
                res_skills = extract_skills_categorized(row["Raw"])["hard"]
                row_data = {"Candidate": row["Name"]}
                for s in top_jd_skills:
                    row_data[s] = 1 if s in res_skills else 0
                heatmap_data.append(row_data)
            
            hdf = pd.DataFrame(heatmap_data)
            fig_heat = px.imshow(
                hdf.set_index("Candidate"),
                labels=dict(x="Required Skill", y="Candidate", color="Match"),
                color_continuous_scale=[[0, "#1e293b"], [1, "#10b981"]],
                template="plotly_dark",
                aspect="auto"
            )
            fig_heat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_heat, use_container_width=True)

    with tab_comparison:
        st.subheader("⚖️ Side-by-Side Talent Comparison")
        if len(df) < 2:
            st.info("Upload at least 2 resumes to enable comparison mode.")
        else:
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                cand1 = st.selectbox("Select Candidate A", df["Name"].tolist(), index=0)
            with c_col2:
                cand2 = st.selectbox("Select Candidate B", df["Name"].tolist(), index=1 if len(df) > 1 else 0)
            
            if cand1 and cand2:
                row1 = df[df["Name"] == cand1].iloc[0]
                row2 = df[df["Name"] == cand2].iloc[0]
                
                comp_col1, comp_col2 = st.columns(2)
                for r, c in [(row1, comp_col1), (row2, comp_col2)]:
                    with c:
                        st.markdown(f"""
                        <div class="glass-card" style="padding:20px;">
                            <h4 style="color:#6366f1;">{r['Name']}</h4>
                            <p style="font-size:1.5rem; font-weight:800;">{r['Score']:.4f}</p>
                            <hr style="opacity:0.1">
                            <p><b>Skills:</b> {r['Skills']:.2f}</p>
                            <p><b>Experience:</b> {r['Experience']:.2f}</p>
                            <p><b>Education:</b> {r['Education']:.2f}</p>
                            <p><b>Training:</b> {r['Training']:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        analysis = analyze_gaps_platinum(job_desc, r["Raw"])
                        st.write("**Top Matches:**")
                        st.markdown(" ".join([f'<span class="skill-badge matched-badge">{s}</span>' for s in analysis["matched_hard"][:8]]), unsafe_allow_html=True)
                        st.write("**Critical Gaps:**")
                        st.markdown(" ".join([f'<span class="skill-badge gap-critical">{s}</span>' for s in analysis["critical_gaps"][:5]]), unsafe_allow_html=True)



    with tab_gaps:
        st.subheader("🚩 Platinum Gap Intelligence")
        st.info("The system separates technical gaps into 'Critical' (no background) and 'Partial' (semantically related coverage found).")
        for _, row in df.iterrows():
            analysis = analyze_gaps_platinum(job_desc, row["Raw"])
            with st.expander(f"Gap Analysis: {row['Name']}"):
                col_m, col_g = st.columns(2)
                with col_m:
                    st.markdown("##### ✅ Matched Skill Entities")
                    st.markdown("".join([f'<span class="skill-badge matched-badge">{m}</span>' for m in analysis["matched_hard"]]), unsafe_allow_html=True)
                    if analysis["matched_soft"]:
                        st.markdown("<p style='font-size:0.7rem; color:#64748b; margin-top:10px;'>SOFT SKILLS MATCHED</p>", unsafe_allow_html=True)
                        st.markdown("".join([f'<span class="skill-badge soft-badge">{m}</span>' for m in analysis["matched_soft"]]), unsafe_allow_html=True)
                with col_g:
                    st.markdown("##### 🚩 Analysis Gaps")
                    if analysis["critical_gaps"]:
                        st.markdown("<p style='font-size:0.7rem; color:#ef4444; font-weight:700;'>CRITICAL GAPS (High Priority)</p>", unsafe_allow_html=True)
                        st.markdown("".join([f'<span class="skill-badge gap-critical">{m}</span>' for m in analysis["critical_gaps"]]), unsafe_allow_html=True)
                    if analysis["partial_matches"]:
                        st.markdown("<p style='font-size:0.7rem; color:#f59e0b; font-weight:700; margin-top:15px;'>PARTIAL MATCHES (Semantically Covered)</p>", unsafe_allow_html=True)
                        for item in analysis["partial_matches"]:
                            st.markdown(f'<span class="skill-badge gap-partial" title="Relates to {item["covered_by"]} ({item["confidence"]:.2f})">{item["gap"]}</span>', unsafe_allow_html=True)
                    if not analysis["critical_gaps"] and not analysis["partial_matches"]:
                        st.success("Full technical alignment detected.")

    with tab_training:
        st.subheader("🎓 Upskilling & Growth Roadmap")
        st.markdown("<p style='color:#64748b; margin-bottom:2rem;'>Personalized training recommendations to bridge critical skill gaps.</p>", unsafe_allow_html=True)
        
        for _, row in df.iterrows():
            analysis = analyze_gaps_platinum(job_desc, row["Raw"])
            with st.expander(f"Growth Strategy: {row['Name']}"):
                col_t1, col_t2 = st.columns([1, 1])
                
                with col_t1:
                    st.markdown("##### 📜 Existing Certifications")
                    if row["TrainingSec"]:
                        st.markdown(f'<div style="background:rgba(99,102,241,0.05); padding:15px; border-radius:12px; border:1px solid rgba(99,102,241,0.1); color:#94a3b8; font-size:0.9rem;">{row["TrainingSec"]}</div>', unsafe_allow_html=True)
                    else:
                        st.info("No explicit certifications detected in resume.")
                
                with col_t2:
                    st.markdown("##### 🚀 Recommended Path")
                    if analysis["critical_gaps"]:
                        recs = get_recommendations(analysis["critical_gaps"])
                        for rec in recs:
                            st.markdown(f"**Skill: {rec['skill'].upper()}**")
                            for course in rec["courses"]:
                                st.markdown(f"""
                                <div style="margin-bottom:10px; padding:10px; background:rgba(255,255,255,0.03); border-radius:8px;">
                                    <div style="font-size:0.85rem; font-weight:600;">{course['title']}</div>
                                    <div style="font-size:0.75rem; color:#64748b;">{course['platform']} • <a href="{course['link']}" target="_blank" style="color:#6366f1;">View Course</a></div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.success("Candidate is highly qualified. Consider advanced leadership or specialized architecture training.")

    with tab_interviewer:
        st.subheader("🎙️ Platinum Interview Intelligence Studio")
        st.markdown("<p style='color:#64748b; margin-bottom:2rem;'>Hyper-targeted discovery protocols derived from semantic gap analysis and role requirements.</p>", unsafe_allow_html=True)
        
        for i, row in df.iterrows():
            analysis = analyze_gaps_platinum(job_desc, row["Raw"])
            with st.expander(f"Strategic Protocol: {row['Name']}"):
                
                # ── Phase 1: Technical Validation ──────────────────────────────────
                st.markdown("### 🧬 Phase 1: Technical DNA Validation")
                col_q1, col_q2 = st.columns(2)
                
                with col_q1:
                    if analysis["critical_gaps"]:
                        g = analysis["critical_gaps"][0].upper()
                        st.markdown(f"""
                        <div class="interview-card">
                            <p style="font-size:0.7rem; color:#6366f1; font-weight:800; letter-spacing:0.1em; margin-bottom:8px;">CRITICAL GAP PROBE</p>
                            <p style="font-weight:600;">"The role requires mastery of {g}. How have you handled transitions into new tech stacks in the past, and what parallel architectures have you built?"</p>
                            <div class="hint-box">✅ LOOK FOR: Ability to map concepts from similar tools, self-learning speed.</div>
                            <div class="warning-box">🚩 RED FLAG: Generic answers or lack of concrete parallel examples.</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="interview-card">
                            <p style="font-size:0.7rem; color:#10b981; font-weight:800; letter-spacing:0.1em; margin-bottom:8px;">ADVANCED DEPTH PROBE</p>
                            <p style="font-weight:600;">"You have a strong technical match. Can you describe the most difficult edge case you solved using your core skills?"</p>
                            <div class="hint-box">✅ LOOK FOR: Deep architectural understanding beyond syntax.</div>
                        </div>
                        """, unsafe_allow_html=True)

                with col_q2:
                    if analysis["partial_matches"]:
                        pm = analysis["partial_matches"][0]
                        st.markdown(f"""
                        <div class="interview-card" style="border-left-color:#f59e0b;">
                            <p style="font-size:0.7rem; color:#f59e0b; font-weight:800; letter-spacing:0.1em; margin-bottom:8px;">SEMANTIC BRIDGE PROBE</p>
                            <p style="font-weight:600;">"We see your expertise in {pm['covered_by'].upper()}. How would you translate those principles to our requirement for {pm['gap'].upper()}?"</p>
                            <div class="hint-box">✅ LOOK FOR: Conceptual agility and understanding of underlying patterns.</div>
                        </div>
                        """, unsafe_allow_html=True)

                # ── Phase 2: Situational Simulation ───────────────────────────────
                st.markdown("### 🎭 Phase 2: Situational Intelligence")
                
                # Dynamic Scenario Generation
                scenario = "scaling a high-traffic system" if "scale" in job_desc.lower() or "senior" in job_desc.lower() else "debugging a critical production issue"
                if "react" in job_desc.lower() or "frontend" in job_desc.lower(): scenario = "optimizing state management for a complex UI"
                
                st.markdown(f"""
                <div class="interview-card" style="border-left-color:#8b5cf6;">
                    <p style="font-size:0.7rem; color:#8b5cf6; font-weight:800; letter-spacing:0.1em; margin-bottom:8px;">DYNAMIC SCENARIO</p>
                    <p style="font-weight:600;">"Scenario: You are tasked with {scenario}. Walk us through your thought process from discovery to implementation. What trade-offs would you make?"</p>
                    <div class="hint-box">✅ LOOK FOR: Systems thinking, awareness of trade-offs, and prioritization logic.</div>
                </div>
                """, unsafe_allow_html=True)

                # ── Phase 3: Leadership & Cultural ────────────────────────────────
                st.markdown("### 👑 Phase 3: Strategic Influence")
                col_l1, col_l2 = st.columns(2)
                
                with col_l1:
                    st.markdown(f"""
                    <div class="interview-card" style="border-left-color:#ec4899;">
                        <p style="font-size:0.7rem; color:#ec4899; font-weight:800; letter-spacing:0.1em; margin-bottom:8px;">BEHAVIORAL DNA</p>
                        <p style="font-weight:600;">"Tell us about a time you disagreed with a technical direction. How did you advocate for your position while maintaining team cohesion?"</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_l2:
                    st.markdown(f"""
                    <div class="interview-card" style="border-left-color:#06b6d4;">
                        <p style="font-size:0.7rem; color:#06b6d4; font-weight:800; letter-spacing:0.1em; margin-bottom:8px;">CONTINUOUS LEARNING</p>
                        <p style="font-weight:600;">"The tech landscape for this role evolves daily. What is the last major technical concept you mastered entirely on your own?"</p>
                    </div>
                    """, unsafe_allow_html=True)

                # ── Decision Scorecard ──────────────────────────────────────────
                st.markdown("### 📝 Interviewer's Private Scorecard")
                score_col1, score_col2, score_col3 = st.columns(3)
                with score_col1: st.select_slider(f"Technical Rigor: {row['Name']}", ["Low", "Med", "High", "Expert"], key=f"s1_{row['Name']}_{i}")
                with score_col2: st.select_slider(f"Comm. Clarity: {row['Name']}", ["Low", "Med", "High", "Expert"], key=f"s2_{row['Name']}_{i}")
                with score_col3: st.select_slider(f"Strategic Fit: {row['Name']}", ["Low", "Med", "High", "Expert"], key=f"s3_{row['Name']}_{i}")

    with tab_raw:
        st.subheader("📄 Text Extraction Nodes")
        for _, row in df.iterrows():
            with st.expander(f"Node Preview: {row['Name']}"):
                st.text_area("Content", row["Raw"], height=300, disabled=True, key=f"pv_{row['Name']}")

st.markdown("<center style='color:#64748b; font-size:0.8rem; margin-top:60px;'>RESUME INTELLIGENCE v3.2.0 • ENTITY-DRIVEN TALENT DISCOVERY • PLATINUM EDITION</center>", unsafe_allow_html=True)