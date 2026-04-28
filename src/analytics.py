import pandas as pd
from sentence_transformers import util
from .ranker import get_model, clean_text
from .skill_extractor import extract_skills_categorized

def analyze_gaps_platinum(job_desc, resume_text):
    jd_entities = extract_skills_categorized(job_desc)
    res_entities = extract_skills_categorized(resume_text)
    
    jd_hard = jd_entities["hard"]
    res_hard = res_entities["hard"]
    
    matched_hard = jd_hard.intersection(res_hard)
    gaps = jd_hard - res_hard
    
    partial_matches = []
    critical_gaps = []
    
    if gaps and res_hard:
        model = get_model()
        gap_list = list(gaps)
        res_list = list(res_hard)
        
        gap_embeddings = model.encode(gap_list, convert_to_tensor=True)
        res_embeddings = model.encode(res_list, convert_to_tensor=True)
        
        sim_matrix = util.cos_sim(gap_embeddings, res_embeddings)
        
        for i, gap in enumerate(gap_list):
            best_sim, best_idx = sim_matrix[i].max().item(), sim_matrix[i].argmax().item()
            if best_sim > 0.75:
                partial_matches.append({
                    "gap": gap,
                    "covered_by": res_list[best_idx],
                    "confidence": best_sim
                })
            else:
                critical_gaps.append(gap)
    else:
        critical_gaps = list(gaps)
        
    return {
        "matched_hard": list(matched_hard),
        "matched_soft": list(jd_entities["soft"].intersection(res_entities["soft"])),
        "critical_gaps": critical_gaps,
        "partial_matches": partial_matches
    }

def get_verdict(score):
    if score > 0.85: return "Elite Match", "verdict-high"
    if score > 0.70: return "Strong Potential", "verdict-med"
    return "Low Alignment", "verdict-low"
