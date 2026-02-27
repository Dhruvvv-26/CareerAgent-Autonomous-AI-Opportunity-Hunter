"""
Scoring Agent — computes match scores and categorizes jobs.
"""

import logging
from sqlalchemy.orm import Session

from database.models import Job
from utils.skill_matcher import match_skills
from utils.reputation_score import get_reputation_score
from utils.confidence_calculator import calculate_confidence

logger = logging.getLogger(__name__)


def _domain_match_score(profile_domains: list[str], job_skills_str: str) -> float:
    """Compute a simple domain overlap score (0-100)."""
    if not profile_domains:
        return 50.0
    job_lower = job_skills_str.lower()
    matches = sum(1 for d in profile_domains if d.lower() in job_lower)
    return (matches / len(profile_domains)) * 100 if profile_domains else 50.0


def _experience_match_score(profile_level: str, role: str) -> float:
    """Estimate how well the experience level fits the role."""
    role_lower = role.lower()
    level = profile_level.lower()

    # Intern/junior roles match entry level best
    if any(kw in role_lower for kw in ["intern", "junior", "trainee", "fresher"]):
        return 100.0 if level == "entry" else 60.0
    # Senior roles match senior level
    if any(kw in role_lower for kw in ["senior", "lead", "principal", "staff"]):
        return 100.0 if level == "senior" else 50.0
    # Mid-level or generic roles
    return 80.0


def _categorize(confidence: float) -> str:
    """Categorize based on confidence score."""
    if confidence > 80:
        return "High Priority"
    elif confidence >= 60:
        return "Good Match"
    else:
        return "Stretch"


def score_jobs(profile: dict, db: Session) -> int:
    """
    Score ALL jobs in the database against the current profile.
    Re-scores on every run so the dashboard always reflects the latest resume.
    Preserves manually set statuses (Applied, Interview, Rejected, Accepted, Emailed).
    Returns number of jobs scored.
    """
    MANUAL_STATUSES = {"Applied", "Interview", "Rejected", "Accepted", "Emailed", "Not Applied"}

    user_skills = [s.lower() for s in profile.get("skills", [])]
    user_domains = profile.get("domains", [])
    experience_level = profile.get("experience_level", "Entry")

    jobs = db.query(Job).all()
    scored_count = 0

    for job in jobs:
        required = [s.strip().lower() for s in job.required_skills.split(",") if s.strip()]

        # Skill match
        _, skill_score = match_skills(user_skills, required)

        # Domain match
        domain_score = _domain_match_score(user_domains, job.required_skills)

        # Experience match
        exp_score = _experience_match_score(experience_level, job.role)

        # Confidence
        confidence = calculate_confidence(skill_score, domain_score, exp_score)

        # Reputation
        reputation = get_reputation_score(job.company)

        # Update scores always
        job.confidence_score = round(confidence, 2)
        job.reputation_score = round(reputation, 2)

        # Only update category if the status hasn't been manually changed
        if job.status not in MANUAL_STATUSES:
            job.status = _categorize(confidence)

        scored_count += 1

    db.commit()
    logger.info(f"Scored {scored_count} jobs.")
    return scored_count

