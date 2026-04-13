import re

def extract_sections(text):
    text = text.lower()

    # Patterns for sections
    skills_pattern = r"(skills|technical skills)(.*?)(experience|education|projects|$)"
    experience_pattern = r"(experience|work experience)(.*?)(education|skills|projects|$)"
    education_pattern = r"(education|academic)(.*?)(experience|skills|projects|$)"

    skills = ""
    experience = ""
    education = ""

    # Extract skills
    match = re.search(skills_pattern, text, re.DOTALL)
    if match:
        skills = match.group(2)

    # Extract experience
    match = re.search(experience_pattern, text, re.DOTALL)
    if match:
        experience = match.group(2)

    # Extract education
    match = re.search(education_pattern, text, re.DOTALL)
    if match:
        education = match.group(2)

    return skills.strip(), experience.strip(), education.strip()