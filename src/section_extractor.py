import re

def extract_sections(text):
    text = text.lower()

    skills_pattern = r"(skills|technical skills)(.*?)(experience|education|projects|training|$)"
    experience_pattern = r"(experience|work experience)(.*?)(education|skills|projects|training|$)"
    education_pattern = r"(education|academic)(.*?)(experience|skills|projects|training|$)"
    training_pattern = r"(certifications|training|courses)(.*?)(experience|skills|projects|education|$)"

    skills = ""
    experience = ""
    education = ""
    training = ""

    match = re.search(skills_pattern, text, re.DOTALL)
    if match:
        skills = match.group(2)

    match = re.search(experience_pattern, text, re.DOTALL)
    if match:
        experience = match.group(2)

    match = re.search(education_pattern, text, re.DOTALL)
    if match:
        education = match.group(2)
        
    match = re.search(training_pattern, text, re.DOTALL)
    if match:
        training = match.group(2)

    return skills.strip(), experience.strip(), education.strip(), training.strip()