from sentence_transformers import SentenceTransformer, util
from preprocess import clean_text
from skill_extractor import extract_skills_categorized
import torch

# Initialize model (cached)
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def compute_semantic_similarity(text1, text2):
    """Compute cosine similarity between two texts using SBERT embeddings."""
    if not text1.strip() or not text2.strip():
        return 0.0
    try:
        model = get_model()
        embeddings = model.encode([text1, text2], convert_to_tensor=True)
        return util.cos_sim(embeddings[0], embeddings[1]).item()
    except Exception:
        return 0.0

def calculate_entity_match(jd_text, resume_text):
    """
    Calculates match scores based on technical entities.
    Hard skills are prioritized over soft skills.
    """
    jd_skills = extract_skills_categorized(jd_text)
    res_skills = extract_skills_categorized(resume_text)
    
    # 1. Hard Skill Match (Strict technical alignment)
    jd_hard = jd_skills["hard"]
    res_hard = res_skills["hard"]
    
    hard_score = 1.0
    if jd_hard:
        hard_score = len(jd_hard & res_hard) / len(jd_hard)
        
    # 2. Soft Skill Match (Lower weight)
    jd_soft = jd_skills["soft"]
    res_soft = res_skills["soft"]
    
    soft_score = 1.0
    if jd_soft:
        soft_score = len(jd_soft & res_soft) / len(jd_soft)
        
    # Return weighted entity score (80% Hard, 20% Soft)
    return (0.8 * hard_score) + (0.2 * soft_score)

def get_semantic_coverage(missing_skill, resume_skills):
    """
    Checks if a missing skill is semantically covered by other skills in the resume.
    Example: Missing 'Django' but has 'Flask' (similarity > 0.7).
    """
    if not resume_skills:
        return 0.0, None
    
    model = get_model()
    skill_embedding = model.encode(missing_skill, convert_to_tensor=True)
    resume_embeddings = model.encode(list(resume_skills), convert_to_tensor=True)
    
    similarities = util.cos_sim(skill_embedding, resume_embeddings)[0]
    best_score, best_idx = torch.max(similarities, dim=0)
    
    return best_score.item(), list(resume_skills)[best_idx.item()]

def rank_resumes(job_desc, resumes, weights=None):
    """
    Ranks resumes using a hybrid of Entity Match and Semantic Similarity.
    """
    if weights is None:
        # Defaults
        weights = {"skills": 0.5, "experience": 0.3, "education": 0.1, "training": 0.1}

    job_clean = clean_text(job_desc)
    results = []

    for i, resume_raw in enumerate(resumes):
        parts = resume_raw.split("|")
        
        # Determine number of parts and assign accordingly
        if len(parts) < 3:
            # Fallback for old/malformed formats
            semantic_score = compute_semantic_similarity(job_clean, clean_text(resume_raw))
            entity_score = calculate_entity_match(job_desc, resume_raw)
            final_score = (0.6 * semantic_score) + (0.4 * entity_score)
            results.append((i, final_score, {"skills": final_score, "experience": 0, "education": 0, "training": 0}))
            continue

        # Map parts to variables (handle 3 or 4 parts)
        skills_text = parts[0]
        exp_text = parts[1]
        edu_text = parts[2]
        train_text = parts[3] if len(parts) > 3 else ""
        
        # 1. Semantic Scores (Concept based)
        skill_semantic = compute_semantic_similarity(job_clean, clean_text(skills_text))
        exp_semantic   = compute_semantic_similarity(job_clean, clean_text(exp_text))
        edu_semantic   = compute_semantic_similarity(job_clean, clean_text(edu_text))
        train_semantic = compute_semantic_similarity(job_clean, clean_text(train_text)) if train_text else 0.0

        # 2. Entity Match (Hard skill matching)
        entity_match_score = calculate_entity_match(job_desc, skills_text)

        # 3. Enhanced Skill Score (Hybrid)
        technical_score = (0.7 * entity_match_score) + (0.3 * skill_semantic)

        # Final Weighted score
        final_score = (
            weights.get("skills", 0) * technical_score +
            weights.get("experience", 0) * exp_semantic +
            weights.get("education", 0) * edu_semantic +
            weights.get("training", 0) * train_semantic
        )

        results.append((i, final_score, {
            "skills": technical_score,
            "experience": exp_semantic,
            "education": edu_semantic,
            "training": train_semantic
        }))

    return sorted(results, key=lambda x: x[1], reverse=True)