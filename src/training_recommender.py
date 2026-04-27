# Training & Courses Intelligence Database
TRAINING_MAP = {
    "python": [
        {"title": "Python for Everybody Specialization", "platform": "Coursera", "link": "https://www.coursera.org/specializations/python"},
        {"title": "Complete Python Bootcamp", "platform": "Udemy", "link": "https://www.udemy.com/course/complete-python-bootcamp/"}
    ],
    "react": [
        {"title": "React - The Complete Guide", "platform": "Udemy", "link": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"},
        {"title": "Modern React with Redux", "platform": "Udemy", "link": "https://www.udemy.com/course/react-redux/"}
    ],
    "machine learning": [
        {"title": "Machine Learning Specialization", "platform": "Coursera", "link": "https://www.coursera.org/specializations/machine-learning-introduction"},
        {"title": "Machine Learning A-Z", "platform": "Udemy", "link": "https://www.udemy.com/course/machinelearning/"}
    ],
    "aws": [
        {"title": "AWS Certified Solutions Architect", "platform": "A Cloud Guru", "link": "https://acloudguru.com/course/aws-certified-solutions-architect-associate-saa-c03"},
        {"title": "Ultimate AWS Certified Solutions Architect Associate", "platform": "Udemy", "link": "https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/"}
    ],
    "docker": [
        {"title": "Docker and Kubernetes: The Complete Guide", "platform": "Udemy", "link": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/"}
    ],
    "kubernetes": [
        {"title": "Certified Kubernetes Administrator (CKA)", "platform": "Udemy", "link": "https://www.udemy.com/course/certified-kubernetes-administrator-with-practice-tests/"}
    ],
    "django": [
        {"title": "Django for Beginners", "platform": "Django for Beginners", "link": "https://djangoforbeginners.com/"}
    ],
    "sql": [
        {"title": "SQL for Data Science", "platform": "Coursera", "link": "https://www.coursera.org/learn/sql-for-data-science"}
    ],
    "java": [
        {"title": "Java Programming Masterclass", "platform": "Udemy", "link": "https://www.udemy.com/course/java-the-complete-java-developer-course/"}
    ],
    "javascript": [
        {"title": "The Complete JavaScript Course", "platform": "Udemy", "link": "https://www.udemy.com/course/the-complete-javascript-course/"}
    ]
}

def get_recommendations(skills):
    """Returns a list of recommended courses for the given skills."""
    recommendations = []
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in TRAINING_MAP:
            recommendations.append({"skill": skill, "courses": TRAINING_MAP[skill_lower]})
        else:
            # Generic search link
            recommendations.append({
                "skill": skill, 
                "courses": [{"title": f"Mastering {skill}", "platform": "Search on Coursera", "link": f"https://www.coursera.org/search?query={skill}"}]
            })
    return recommendations
