import re

# predefined skill list (you can expand)
SKILLS_DB = [
    "python", "java", "sql", "machine learning", "data structures",
    "algorithms", "c++", "javascript", "react", "nodejs",
    "spring", "django", "flask", "html", "css"
]

def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS_DB:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found_skills.append(skill)

    return " ".join(found_skills)