"""
Jobs Router — search, list, filter, stats, update statuses, email preview & send.
"""

import json
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Job, ResumeProfile
from agents.search_agent import search_jobs
from agents.scoring_agent import score_jobs
from agents.email_agent import send_cold_email, get_email_preview

router = APIRouter()


def _get_profile(db: Session) -> dict | None:
    """Retrieve the stored resume profile."""
    profile = db.query(ResumeProfile).first()
    if not profile:
        return None
    return {
        "skills": json.loads(profile.skills),
        "domains": json.loads(profile.domains),
        "experience_level": profile.experience_level,
        "preferred_roles": json.loads(profile.preferred_roles),
    }


@router.post("/run-search")
def run_search(db: Session = Depends(get_db)):
    """
    Trigger the search + scoring pipeline.
    Requires a resume profile to be uploaded first.
    """
    profile = _get_profile(db)
    if not profile:
        return {"error": "No resume profile found. Please upload a resume first."}

    new_jobs = search_jobs(profile, db)
    scored = score_jobs(profile, db)

    return {
        "message": f"Search complete. {len(new_jobs)} new jobs found, {scored} scored.",
        "new_jobs_count": len(new_jobs),
        "scored_count": scored,
    }


@router.get("/jobs")
def get_jobs(
    category: str = Query(None, description="Filter by category"),
    source: str = Query(None, description="Filter by source portal"),
    db: Session = Depends(get_db),
):
    """Return all jobs with recruiter email info."""
    query = db.query(Job)
    if category:
        query = query.filter(Job.status == category)
    if source:
        query = query.filter(Job.source == source)

    jobs = query.order_by(Job.confidence_score.desc()).all()

    return [
        {
            "id": job.id,
            "company": job.company,
            "role": job.role,
            "location": job.location,
            "stipend": job.stipend,
            "required_skills": job.required_skills,
            "deadline": job.deadline,
            "link": job.link,
            "confidence_score": job.confidence_score,
            "reputation_score": job.reputation_score,
            "status": job.status,
            "source": job.source or "Unknown",
            "date_added": str(job.date_added),
            "recruiter_email": job.recruiter_email or "",
        }
        for job in jobs
    ]


@router.get("/job-stats")
def get_job_stats(db: Session = Depends(get_db)):
    """Return aggregate counts for dashboard filter badges."""
    category_counts_raw = (
        db.query(Job.status, func.count(Job.id))
        .group_by(Job.status)
        .all()
    )
    category_counts = {status: count for status, count in category_counts_raw}

    source_counts_raw = (
        db.query(Job.source, func.count(Job.id))
        .group_by(Job.source)
        .all()
    )
    source_counts = {source or "Unknown": count for source, count in source_counts_raw}

    total = db.query(func.count(Job.id)).scalar() or 0

    return {
        "total": total,
        "by_category": category_counts,
        "by_source": source_counts,
    }


@router.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    """Return the current resume profile with contact info."""
    profile_row = db.query(ResumeProfile).first()
    if not profile_row:
        return {"error": "No resume profile found. Upload a resume first."}

    return {
        "profile": {
            "skills": json.loads(profile_row.skills),
            "domains": json.loads(profile_row.domains),
            "experience_level": profile_row.experience_level,
            "preferred_roles": json.loads(profile_row.preferred_roles),
            "contact_info": {
                "full_name": profile_row.full_name or "",
                "email": profile_row.email or "",
                "phone": profile_row.phone or "",
                "linkedin_url": profile_row.linkedin_url or "",
                "github_url": profile_row.github_url or "",
            },
        }
    }


@router.put("/update-status/{job_id}")
def update_status(job_id: int, status: str = Query(...), db: Session = Depends(get_db)):
    """Update the status of a specific job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"error": "Job not found."}

    job.status = status
    db.commit()

    return {"message": f"Job {job_id} status updated to '{status}'."}


@router.put("/update-recruiter-email/{job_id}")
def update_recruiter_email(
    job_id: int,
    email: str = Query(..., description="Recruiter email address"),
    db: Session = Depends(get_db),
):
    """Manually set the recruiter email for a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"error": "Job not found."}

    job.recruiter_email = email
    db.commit()

    return {"message": f"Recruiter email for job {job_id} updated to '{email}'."}


@router.get("/email-preview/{job_id}")
def email_preview(job_id: int, db: Session = Depends(get_db)):
    """
    Generate an email preview for a specific job.
    Returns subject, body, to, from, contact info for the frontend modal.
    """
    profile = _get_profile(db)
    if not profile:
        return {"error": "No resume profile found. Please upload a resume first."}

    return get_email_preview(job_id, profile, db)


class SendEmailRequest(BaseModel):
    job_id: int
    to: str = ""
    subject: str = ""
    body: str = ""


@router.post("/send-email")
def trigger_send_email(req: SendEmailRequest = None, db: Session = Depends(get_db)):
    """
    Send a cold email for a specific job.
    Accepts optional overrides for to, subject, body from the preview editor.
    """
    profile = _get_profile(db)
    if not profile:
        return {"error": "No resume profile found. Please upload a resume first."}

    if req and req.job_id:
        result = send_cold_email(
            db=db,
            profile=profile,
            job_id=req.job_id,
            to_email=req.to or None,
            subject=req.subject or None,
            body=req.body or None,
        )
    else:
        result = send_cold_email(db=db, profile=profile)

    return result
