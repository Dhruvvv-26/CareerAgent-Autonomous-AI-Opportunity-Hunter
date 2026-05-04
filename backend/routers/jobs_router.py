"""
Jobs Router — search, list, filter, stats, update statuses, email preview & send,
export CSV, delete/archive, bookmarks, status history, and email logs.
"""

import csv
import io
import json
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Job, ResumeProfile, JobStatusHistory, EmailLog
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
    bookmarked: bool = Query(None, description="Filter bookmarked jobs"),
    show_archived: bool = Query(False, description="Include archived jobs"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=200, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Return paginated jobs with recruiter email info."""
    query = db.query(Job)

    if not show_archived:
        query = query.filter(Job.archived == False)
    if category:
        query = query.filter(Job.status == category)
    if source:
        query = query.filter(Job.source == source)
    if bookmarked is not None:
        query = query.filter(Job.bookmarked == bookmarked)

    total = query.count()
    total_pages = max(1, (total + per_page - 1) // per_page)

    jobs = (
        query.order_by(Job.confidence_score.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "jobs": [
            {
                "id": job.id,
                "company": job.company,
                "role": job.role,
                "location": job.location,
                "stipend": job.stipend,
                "required_skills": job.required_skills,
                "job_description": job.job_description or "",
                "deadline": job.deadline,
                "link": job.link,
                "confidence_score": job.confidence_score,
                "reputation_score": job.reputation_score,
                "status": job.status,
                "source": job.source or "Unknown",
                "date_added": str(job.date_added),
                "recruiter_email": job.recruiter_email or "",
                "bookmarked": job.bookmarked,
                "archived": job.archived,
            }
            for job in jobs
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    }


@router.get("/job-stats")
def get_job_stats(db: Session = Depends(get_db)):
    """Return aggregate counts for dashboard filter badges."""
    base = db.query(Job).filter(Job.archived == False)

    category_counts_raw = (
        base.with_entities(Job.status, func.count(Job.id))
        .group_by(Job.status)
        .all()
    )
    category_counts = {status: count for status, count in category_counts_raw}

    source_counts_raw = (
        base.with_entities(Job.source, func.count(Job.id))
        .group_by(Job.source)
        .all()
    )
    source_counts = {source or "Unknown": count for source, count in source_counts_raw}

    # Daily trend — jobs added per day (last 30 entries)
    daily_trend_raw = (
        db.query(Job.date_added, func.count(Job.id))
        .group_by(Job.date_added)
        .order_by(Job.date_added.desc())
        .limit(30)
        .all()
    )
    daily_trend = [
        {"date": str(d), "count": c} for d, c in reversed(daily_trend_raw)
    ]

    total = base.count()
    bookmarked_count = base.filter(Job.bookmarked == True).count()

    return {
        "total": total,
        "bookmarked": bookmarked_count,
        "by_category": category_counts,
        "by_source": source_counts,
        "daily_trend": daily_trend,
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
    """Update the status of a specific job and record in history."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"error": "Job not found."}

    old_status = job.status

    # Record status change history
    history = JobStatusHistory(
        job_id=job.id,
        old_status=old_status,
        new_status=status,
        changed_at=datetime.utcnow(),
    )
    db.add(history)

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


# ---------------------------------------------------------------------------
# Bookmark endpoints
# ---------------------------------------------------------------------------
@router.put("/toggle-bookmark/{job_id}")
def toggle_bookmark(job_id: int, db: Session = Depends(get_db)):
    """Toggle the bookmarked state of a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"error": "Job not found."}

    job.bookmarked = not job.bookmarked
    db.commit()

    return {
        "message": f"Job {job_id} {'bookmarked' if job.bookmarked else 'unbookmarked'}.",
        "bookmarked": job.bookmarked,
    }


# ---------------------------------------------------------------------------
# Delete / Archive endpoints
# ---------------------------------------------------------------------------
@router.put("/archive-job/{job_id}")
def archive_job(job_id: int, db: Session = Depends(get_db)):
    """Archive (soft-delete) a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"error": "Job not found."}

    job.archived = not job.archived
    db.commit()

    return {
        "message": f"Job {job_id} {'archived' if job.archived else 'restored'}.",
        "archived": job.archived,
    }


@router.delete("/delete-job/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Permanently delete a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"error": "Job not found."}

    db.delete(job)
    db.commit()

    return {"message": f"Job {job_id} permanently deleted."}


# ---------------------------------------------------------------------------
# Status History
# ---------------------------------------------------------------------------
@router.get("/status-history/{job_id}")
def get_status_history(job_id: int, db: Session = Depends(get_db)):
    """Get the status change history for a specific job."""
    history = (
        db.query(JobStatusHistory)
        .filter(JobStatusHistory.job_id == job_id)
        .order_by(JobStatusHistory.changed_at.desc())
        .all()
    )

    return [
        {
            "id": h.id,
            "old_status": h.old_status,
            "new_status": h.new_status,
            "changed_at": h.changed_at.isoformat() if h.changed_at else "",
        }
        for h in history
    ]


# ---------------------------------------------------------------------------
# Email History
# ---------------------------------------------------------------------------
@router.get("/email-history/{job_id}")
def get_email_history(job_id: int, db: Session = Depends(get_db)):
    """Get the email send history for a specific job."""
    logs = (
        db.query(EmailLog)
        .filter(EmailLog.job_id == job_id)
        .order_by(EmailLog.sent_at.desc())
        .all()
    )

    return [
        {
            "id": log.id,
            "to_email": log.to_email,
            "subject": log.subject,
            "sent_at": log.sent_at.isoformat() if log.sent_at else "",
            "status": log.status,
        }
        for log in logs
    ]


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------
@router.get("/export-jobs")
def export_jobs_csv(db: Session = Depends(get_db)):
    """Export all non-archived jobs as a CSV file."""
    jobs = (
        db.query(Job)
        .filter(Job.archived == False)
        .order_by(Job.confidence_score.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        "ID", "Company", "Role", "Location", "Stipend",
        "Confidence %", "Reputation", "Status", "Source",
        "Date Added", "Link", "Recruiter Email", "Bookmarked",
    ])

    for job in jobs:
        writer.writerow([
            job.id, job.company, job.role, job.location, job.stipend,
            job.confidence_score, job.reputation_score, job.status,
            job.source or "Unknown", str(job.date_added),
            job.link, job.recruiter_email or "", "Yes" if job.bookmarked else "No",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=career_agent_jobs.csv"},
    )


# ---------------------------------------------------------------------------
# Email Preview & Send
# ---------------------------------------------------------------------------
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
    Logs the email in EmailLog.
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

    # Log the email if it was sent successfully
    if result.get("status") == "sent":
        email_log = EmailLog(
            job_id=req.job_id if req else 0,
            to_email=result.get("to", ""),
            subject=result.get("subject", ""),
            sent_at=datetime.utcnow(),
            status="sent",
        )
        db.add(email_log)
        db.commit()

    return result
