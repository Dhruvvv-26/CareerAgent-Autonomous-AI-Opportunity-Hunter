"""
Skill Matcher — compares user skills against job-required skills.
"""


def match_skills(
    user_skills: list[str], required_skills: list[str]
) -> tuple[list[str], float]:
    """
    Compute skill match between user and job requirements.

    Args:
        user_skills: list of user skills (lowercase).
        required_skills: list of required skills (lowercase).

    Returns:
        (common_skills, match_score)
        match_score = (len(common) / len(required)) * 100
    """
    if not required_skills:
        return [], 50.0  # neutral if nothing is required

    user_set = set(s.strip().lower() for s in user_skills if s.strip())
    req_set = set(s.strip().lower() for s in required_skills if s.strip())

    common = sorted(user_set & req_set)
    score = (len(common) / len(req_set)) * 100 if req_set else 50.0

    return common, round(score, 2)
