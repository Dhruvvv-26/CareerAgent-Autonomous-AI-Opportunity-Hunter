"""
Resume Agent — extracts skills, contact info, and structured information from a PDF resume.
Uses PyMuPDF for text extraction, keyword matching for skills, and regex for contact info.
"""

import json
import re
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


# ---------------------------------------------------------------------------
# Contact info extraction
# ---------------------------------------------------------------------------
def extract_contact_info(text: str) -> dict:
    """
    Extract personal contact details from resume text using regex.
    Returns: {full_name, email, phone, linkedin_url, github_url}
    """
    result = {
        "full_name": "",
        "email": "",
        "phone": "",
        "linkedin_url": "",
        "github_url": "",
    }

    # --- Email ---
    email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    if emails:
        result["email"] = emails[0]

    # --- Phone (Indian & international) ---
    phone_patterns = [
        r'(?:\+91[\s\-]?)?[6-9]\d{4}[\s\-]?\d{5}',    # Indian: +91 98765 43210
        r'(?:\+91[\s\-]?)?\d{10}',                       # 10-digit
        r'(?:\+\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}',  # International
    ]
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            phone = matches[0].strip()
            # Only accept if it looks like a phone (7+ digits)
            digits = re.sub(r'\D', '', phone)
            if len(digits) >= 10:
                result["phone"] = phone
                break

    # --- LinkedIn URL ---
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_\-/]+'
    linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_matches:
        url = linkedin_matches[0]
        if not url.startswith("http"):
            url = "https://" + url
        result["linkedin_url"] = url

    # --- GitHub URL ---
    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_\-]+'
    github_matches = re.findall(github_pattern, text, re.IGNORECASE)
    if github_matches:
        url = github_matches[0]
        if not url.startswith("http"):
            url = "https://" + url
        result["github_url"] = url

    # --- Full Name (heuristic: first non-empty line that isn't an email/URL/phone) ---
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:5]:  # Check first 5 lines
        # Skip if it's an email, URL, or phone
        if "@" in line or "http" in line or "linkedin" in line.lower():
            continue
        if re.match(r'^[\+\d\s\-\(\)]{10,}$', line):  # Skip phone lines
            continue
        # Likely a name if it's short-ish and mostly alpha
        cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        if cleaned and len(cleaned.split()) <= 5 and len(cleaned) <= 60:
            result["full_name"] = cleaned
            break

    return result


def parse_resume(file_bytes: bytes) -> dict:
    """
    Main entry point: parse a PDF resume and return structured JSON.
    Returns:
        {
            "skills": [...],
            "domains": [...],
            "experience_level": "...",
            "preferred_roles": [...],
            "contact_info": {
                "full_name": "...",
                "email": "...",
                "phone": "...",
                "linkedin_url": "...",
                "github_url": "...",
            }
        }
    """
    text = extract_text_from_pdf(file_bytes)
    skills = detect_skills(text)
    domains = detect_domains(skills)
    experience_level = detect_experience_level(text)
    preferred_roles = detect_preferred_roles(text)
    contact_info = extract_contact_info(text)

    return {
        "skills": skills,
        "domains": domains,
        "experience_level": experience_level,
        "preferred_roles": preferred_roles,
        "contact_info": contact_info,
    }
