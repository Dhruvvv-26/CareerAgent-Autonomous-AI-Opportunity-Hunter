"""
Resume Agent — extracts skills and structured information from a PDF resume.
Uses PyMuPDF for text extraction and keyword matching for skill detection.
"""

import json
import fitz  # PyMuPDF


# ---------------------------------------------------------------------------
# Predefined skill & domain dictionaries
# ---------------------------------------------------------------------------
SKILL_DICTIONARY = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab",
    "perl", "shell", "bash", "sql", "html", "css",
    # Frameworks & Libraries
    "react", "angular", "vue", "node.js", "express", "django", "flask",
    "fastapi", "spring", "rails", "laravel", "next.js", "svelte",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "opencv", "matplotlib", "seaborn",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "jenkins", "github actions", "ci/cd", "linux", "nginx",
    # Data & AI/ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "data science", "data analysis", "data engineering", "big data",
    "spark", "hadoop", "kafka", "airflow", "etl",
    "natural language processing", "reinforcement learning",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "sqlite", "firebase", "dynamodb", "cassandra",
    # Tools & Misc
    "git", "jira", "figma", "postman", "rest api", "graphql",
    "microservices", "agile", "scrum", "power bi", "tableau",
    "excel", "blockchain", "iot", "cybersecurity",
}

DOMAIN_KEYWORDS = {
    "ai/ml": ["machine learning", "deep learning", "nlp", "computer vision",
              "tensorflow", "pytorch", "scikit-learn", "data science"],
    "web development": ["react", "angular", "vue", "node.js", "django",
                        "flask", "fastapi", "html", "css", "javascript"],
    "data engineering": ["spark", "hadoop", "kafka", "airflow", "etl",
                         "big data", "data engineering"],
    "devops": ["docker", "kubernetes", "terraform", "jenkins", "ci/cd",
               "aws", "azure", "gcp"],
    "mobile development": ["swift", "kotlin", "react native", "flutter"],
    "cybersecurity": ["cybersecurity", "penetration testing", "siem"],
    "backend development": ["java", "python", "go", "rust", "c++",
                            "microservices", "rest api", "graphql"],
}

EXPERIENCE_KEYWORDS = {
    "senior": ["senior", "lead", "principal", "staff", "architect",
               "8+ years", "10+ years", "manager"],
    "mid": ["mid", "3+ years", "4+ years", "5+ years", "intermediate"],
    "entry": ["intern", "junior", "entry", "fresher", "graduate",
              "0-1 year", "0-2 years", "trainee"],
}

ROLE_KEYWORDS = {
    "software engineer": ["software engineer", "software developer", "sde"],
    "data scientist": ["data scientist", "ml engineer", "ai engineer"],
    "frontend developer": ["frontend", "front-end", "react developer"],
    "backend developer": ["backend", "back-end", "server-side"],
    "full stack developer": ["full stack", "fullstack"],
    "devops engineer": ["devops", "site reliability", "sre"],
    "data analyst": ["data analyst", "business analyst"],
    "product manager": ["product manager", "product owner"],
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF using PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def detect_skills(text: str) -> list[str]:
    """Match text against the predefined skill dictionary."""
    text_lower = text.lower()
    found = []
    for skill in SKILL_DICTIONARY:
        if skill in text_lower:
            found.append(skill)
    return sorted(set(found))


def detect_domains(skills: list[str]) -> list[str]:
    """Determine domains based on detected skills."""
    domains = []
    skills_lower = [s.lower() for s in skills]
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in skills_lower for kw in keywords):
            domains.append(domain)
    return domains


def detect_experience_level(text: str) -> str:
    """Estimate experience level from resume text."""
    text_lower = text.lower()
    for level, keywords in EXPERIENCE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return level.capitalize()
    return "Entry"


def detect_preferred_roles(text: str) -> list[str]:
    """Identify preferred roles from resume text."""
    text_lower = text.lower()
    roles = []
    for role, keywords in ROLE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            roles.append(role)
    return roles if roles else ["Software Engineer"]


def parse_resume(file_bytes: bytes) -> dict:
    """
    Main entry point: parse a PDF resume and return structured JSON.
    Returns:
        {
            "skills": [...],
            "domains": [...],
            "experience_level": "...",
            "preferred_roles": [...]
        }
    """
    text = extract_text_from_pdf(file_bytes)
    skills = detect_skills(text)
    domains = detect_domains(skills)
    experience_level = detect_experience_level(text)
    preferred_roles = detect_preferred_roles(text)

    return {
        "skills": skills,
        "domains": domains,
        "experience_level": experience_level,
        "preferred_roles": preferred_roles,
    }
