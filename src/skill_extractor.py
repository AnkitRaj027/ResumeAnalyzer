import re

# Structured Skill Intelligence Database
# Categorized for prioritized ranking and gap analysis.
SKILLS_INTEL = {
    "hard_skills": [
        # Languages
        "python", "java", "c", "c++", "c#", "javascript", "typescript", "go", "rust", 
        "kotlin", "swift", "php", "ruby", "scala", "dart", "r", "matlab", "perl", "bash",
        
        # Frontend
        "html", "css", "sass", "less", "react", "angular", "vue", "next.js", "nextjs", 
        "nuxt.js", "nuxtjs", "svelte", "redux", "webpack", "babel", "vite", "jquery", 
        "bootstrap", "tailwind", "material-ui", "chakra ui",
        
        # Backend / Frameworks
        "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring", 
        "spring boot", "laravel", "asp.net", "rails", "phoenix", "nest.js", "nestjs",
        
        # Database
        "sql", "mysql", "postgresql", "sqlite", "mongodb", "firebase", "redis", 
        "oracle", "cassandra", "dynamodb", "neo4j", "elasticsearch", "mariadb",
        
        # AI / Data Science / ML
        "machine learning", "deep learning", "artificial intelligence", "data science", 
        "data analysis", "data visualization", "nlp", "computer vision", "pandas", 
        "numpy", "scikit-learn", "tensorflow", "keras", "pytorch", "xgboost", 
        "lightgbm", "opencv", "nltk", "spacy", "huggingface", "llm", "langchain",
        
        # Big Data
        "hadoop", "spark", "pyspark", "kafka", "hive", "airflow", "snowflake", "databricks",
        
        # Cloud / DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", 
        "ansible", "ci/cd", "github actions", "circleci", "vagrant", "helm", "prometheus", "grafana",
        
        # Concepts / Security
        "data structures", "algorithms", "oops", "object oriented programming", 
        "design patterns", "system design", "microservices", "rest api", "graphql", 
        "grpc", "unit testing", "integration testing", "selenium", "cypress", "playwright", 
        "jest", "mocha", "manual testing", "automation", "cybersecurity", "penetration testing",
        
        # Mobile
        "android", "ios", "react native", "flutter", "xamarin", "ionic", "swiftui"
    ],
    "soft_skills": [
        "communication", "leadership", "problem solving", "teamwork", "management", 
        "agile", "scrum", "kanban", "presentation", "mentoring", "customer service",
        "time management", "critical thinking", "adaptability", "creativity"
    ]
}

def extract_skills_categorized(text):
    """Extracts technical and soft skills as separate sets."""
    if not text:
        return {"hard": set(), "soft": set()}
    
    text = text.lower()
    found = {"hard": set(), "soft": set()}

    # Check Hard Skills
    for skill in SKILLS_INTEL["hard_skills"]:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found["hard"].add(skill)
            
    # Check Soft Skills
    for skill in SKILLS_INTEL["soft_skills"]:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found["soft"].add(skill)

    return found

def extract_skills_as_list(text):
    """Returns all extracted skills as a single unique sorted list."""
    res = extract_skills_categorized(text)
    return sorted(list(res["hard"] | res["soft"]))

def extract_skills(text):
    """Backwards compatibility for space-separated extraction."""
    return " ".join(extract_skills_as_list(text))