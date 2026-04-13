from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import clean_text

def compute_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf[0:1], tfidf[1:])[0][0]


def rank_resumes(job_desc, resumes):

    # Try different weight combinations (optimization)
    weight_options = [
        (0.5, 0.3, 0.2),
        (0.6, 0.3, 0.1),
        (0.7, 0.2, 0.1)
    ]

    best_weights = None
    best_score_sum = -1
    best_ranking = None

    for weights in weight_options:

        temp_ranking = []
        total_score = 0

        for i, resume in enumerate(resumes):

            parts = resume.split("|")
            if len(parts) != 3:
                continue

            skills, experience, education = parts

            job = clean_text(job_desc)
            skills = clean_text(skills)
            experience = clean_text(experience)
            education = clean_text(education)

            skill_score = compute_similarity(job, skills)
            exp_score = compute_similarity(job, experience)
            edu_score = compute_similarity(job, education)

            # APPLY CURRENT WEIGHTS
            final_score = (
                weights[0] * skill_score +
                weights[1] * exp_score +
                weights[2] * edu_score
            )

            temp_ranking.append((i, final_score))
            total_score += final_score

        # Keep best weights
        if total_score > best_score_sum:
            best_score_sum = total_score
            best_weights = weights
            best_ranking = temp_ranking

    print(f"\nBest Weights Found: {best_weights}")

    return sorted(best_ranking, key=lambda x: x[1], reverse=True)