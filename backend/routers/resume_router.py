"""
Resume Router — handles resume upload and profile extraction.
"""

import json
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import ResumeProfile
from agents.resume_agent import parse_resume

router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a PDF resume, extract skills and info, store profile.
    """
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are accepted."}

    file_bytes = await file.read()
    profile = parse_resume(file_bytes)

    # Upsert: keep only the latest profile
    existing = db.query(ResumeProfile).first()
    if existing:
        existing.skills = json.dumps(profile["skills"])
        existing.domains = json.dumps(profile["domains"])
        existing.experience_level = profile["experience_level"]
        existing.preferred_roles = json.dumps(profile["preferred_roles"])
    else:
        db_profile = ResumeProfile(
            skills=json.dumps(profile["skills"]),
            domains=json.dumps(profile["domains"]),
            experience_level=profile["experience_level"],
            preferred_roles=json.dumps(profile["preferred_roles"]),
        )
        db.add(db_profile)

    db.commit()

    return {
        "message": "Resume parsed successfully.",
        "profile": profile,
    }
