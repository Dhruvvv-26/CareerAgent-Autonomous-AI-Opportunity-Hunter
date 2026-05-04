"""
Skill Matcher — TF-IDF based skill matching with cosine similarity.
Falls back to exact matching when scikit-learn is not available.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False
    logger.warning("scikit-learn not installed — falling back to exact skill matching.")


# Synonym normalization map for common aliases
_SYNONYMS = {
    "js": "javascript", "ts": "typescript", "py": "python",
    "node": "node.js", "nodejs": "node.js", "react.js": "react",
    "reactjs": "react", "vue.js": "vue", "vuejs": "vue",
    "angular.js": "angular", "angularjs": "angular",
    "next": "next.js", "nextjs": "next.js",
    "ml": "machine learning", "dl": "deep learning",
    "k8s": "kubernetes", "tf": "tensorflow",
    "aws lambda": "aws", "ec2": "aws", "s3": "aws",
    "gke": "gcp", "bigquery": "gcp",
    "nlp": "natural language processing",
    "cv": "computer vision", "ci/cd": "cicd",
    "postgres": "postgresql", "mongo": "mongodb",
    "sci-kit learn": "scikit-learn", "sklearn": "scikit-learn",
}


def _normalize(skill: str) -> str:
    """Normalize a skill name using the synonym map."""
    s = skill.strip().lower()
    return _SYNONYMS.get(s, s)


def match_skills(
    user_skills: list[str], required_skills: list[str]
) -> tuple[list[str], float]:
    """
    Compute skill match between user and job requirements.

    Uses TF-IDF + cosine similarity for fuzzy matching when available,
    otherwise falls back to exact set intersection.

    Args:
        user_skills: list of user skills (lowercase).
        required_skills: list of required skills (lowercase).

    Returns:
        (common_skills, match_score)
        match_score on a 0–100 scale.
    """
    if not required_skills:
        return [], 50.0  # neutral if nothing is required

    # Normalize skills
    user_normalized = [_normalize(s) for s in user_skills if s.strip()]
    req_normalized = [_normalize(s) for s in required_skills if s.strip()]

    if not user_normalized or not req_normalized:
        return [], 50.0

    # Exact match (always computed)
    user_set = set(user_normalized)
    req_set = set(req_normalized)
    exact_common = sorted(user_set & req_set)
    exact_score = (len(exact_common) / len(req_set)) * 100 if req_set else 50.0

    # TF-IDF fuzzy match
    if _HAS_SKLEARN and len(req_normalized) > 0:
        try:
            user_doc = " ".join(user_normalized)
            req_doc = " ".join(req_normalized)

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([user_doc, req_doc])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            tfidf_score = sim * 100

            # Blend: 60% TF-IDF (fuzzy) + 40% exact match
            blended_score = 0.6 * tfidf_score + 0.4 * exact_score
            return exact_common, round(blended_score, 2)
        except Exception as e:
            logger.debug(f"TF-IDF matching failed, using exact: {e}")

    return exact_common, round(exact_score, 2)
