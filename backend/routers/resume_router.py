"""
Resume Router — handles resume upload, profile extraction, and contact info storage.
"""

import json
import os
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import ResumeProfile
from agents.resume_agent import parse_resume

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a PDF resume, extract skills and contact info, save the PDF file, store profile.
    """
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are accepted."}

    file_bytes = await file.read()
    profile = parse_resume(file_bytes)

    # Save the PDF file to uploads/
    resume_filename = "resume.pdf"
    resume_path = os.path.join(UPLOAD_DIR, resume_filename)
    with open(resume_path, "wb") as f:
        f.write(file_bytes)

    contact = profile.get("contact_info", {})

    # Upsert: keep only the latest profile
    existing = db.query(ResumeProfile).first()
    if existing:
        existing.skills = json.dumps(profile["skills"])
        existing.domains = json.dumps(profile["domains"])
        existing.experience_level = profile["experience_level"]
        existing.preferred_roles = json.dumps(profile["preferred_roles"])
        existing.full_name = contact.get("full_name", "")
        existing.phone = contact.get("phone", "")
        existing.email = contact.get("email", "")
        existing.linkedin_url = contact.get("linkedin_url", "")
        existing.github_url = contact.get("github_url", "")
        existing.resume_file_path = resume_path
    else:
        db_profile = ResumeProfile(
            skills=json.dumps(profile["skills"]),
            domains=json.dumps(profile["domains"]),
            experience_level=profile["experience_level"],
            preferred_roles=json.dumps(profile["preferred_roles"]),
            full_name=contact.get("full_name", ""),
            phone=contact.get("phone", ""),
            email=contact.get("email", ""),
            linkedin_url=contact.get("linkedin_url", ""),
            github_url=contact.get("github_url", ""),
            resume_file_path=resume_path,
        )
        db.add(db_profile)

    db.commit()

    return {
        "message": "Resume parsed successfully.",
        "profile": profile,
    }
