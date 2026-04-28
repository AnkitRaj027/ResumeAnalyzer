import torch
from sentence_transformers import SentenceTransformer, util
from .preprocess import clean_text
from .skill_extractor import extract_skills_categorized

_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def compute_semantic_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0
    model = get_model()
    embeddings = model.encode([text1, text2], convert_to_tensor=True)
    return util.cos_sim(embeddings[0], embeddings[1]).item()

def calculate_entity_match(job_desc, resume_text):
    jd_entities = extract_skills_categorized(job_desc)
    res_entities = extract_skills_categorized(resume_text)
    
    jd_hard = jd_entities["hard"]
    res_hard = res_entities["hard"]
    
    if not jd_hard:
        return 0.0
        
    matched = jd_hard.intersection(res_hard)
    score = len(matched) / len(jd_hard)
    return score

def find_best_semantic_match(missing_skill, resume_skills):
    if not resume_skills:
        return 0.0, None
    
    model = get_model()
    skill_embedding = model.encode(missing_skill, convert_to_tensor=True)
    resume_embeddings = model.encode(list(resume_skills), convert_to_tensor=True)
    
    similarities = util.cos_sim(skill_embedding, resume_embeddings)[0]
    best_score, best_idx = torch.max(similarities, dim=0)
    
    return best_score.item(), list(resume_skills)[best_idx.item()]

def rank_resumes(job_desc, resumes, weights=None):
    if weights is None:
        weights = {"skills": 0.6, "experience": 0.3, "education": 0.1}

    job_clean = clean_text(job_desc)
    results = []

    for i, resume_raw in enumerate(resumes):
        parts = resume_raw.split("|")
        
        if len(parts) < 3:
            semantic_score = compute_semantic_similarity(job_clean, clean_text(resume_raw))
            entity_score = calculate_entity_match(job_desc, resume_raw)
            final_score = (0.6 * semantic_score) + (0.4 * entity_score)
            results.append((i, final_score, {"skills": final_score, "experience": 0, "education": 0}))
            continue

        skills_text, exp_text, edu_text = parts[0], parts[1], parts[2]
        
        skill_semantic = compute_semantic_similarity(job_clean, clean_text(skills_text))
        exp_semantic   = compute_semantic_similarity(job_clean, clean_text(exp_text))
        edu_semantic   = compute_semantic_similarity(job_clean, clean_text(edu_text))

        entity_match_score = calculate_entity_match(job_desc, skills_text)
        technical_score = (0.7 * entity_match_score) + (0.3 * skill_semantic)

        final_score = (
            weights.get("skills", 0) * technical_score +
            weights.get("experience", 0) * exp_semantic +
            weights.get("education", 0) * edu_semantic
        )

        results.append((i, final_score, {
            "skills": technical_score,
            "experience": exp_semantic,
            "education": edu_semantic
        }))

    return sorted(results, key=lambda x: x[1], reverse=True)