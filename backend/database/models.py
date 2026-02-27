"""
SQLAlchemy ORM models for jobs and resume profiles.
"""

from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, Text
from database.db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    location = Column(Text, default="Remote")
    stipend = Column(Text, default="Unpaid")
    required_skills = Column(Text, default="")
    deadline = Column(Text, default="N/A")
    link = Column(Text, default="")
    confidence_score = Column(Float, default=0.0)
    reputation_score = Column(Float, default=0.0)
    status = Column(String(50), default="New")
    date_added = Column(Date, default=date.today)
    source = Column(String(50), default="Unknown")
    job_hash = Column(String(64), unique=True, nullable=False)
    recruiter_email = Column(Text, default="")  # scraped or manually entered


class ResumeProfile(Base):
    __tablename__ = "resume_profiles"

    id = Column(Integer, primary_key=True, index=True)
    skills = Column(Text, default="[]")          # JSON string
    domains = Column(Text, default="[]")          # JSON string
    experience_level = Column(String(50), default="Entry")
    preferred_roles = Column(Text, default="[]")  # JSON string
    uploaded_at = Column(Date, default=date.today)

    # Contact info extracted from resume
    full_name = Column(Text, default="")
    phone = Column(Text, default="")
    email = Column(Text, default="")
    linkedin_url = Column(Text, default="")
    github_url = Column(Text, default="")
    resume_file_path = Column(Text, default="")   # Path to saved PDF
