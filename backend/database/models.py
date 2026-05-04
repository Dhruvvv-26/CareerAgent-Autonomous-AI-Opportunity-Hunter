"""
SQLAlchemy ORM models for jobs, resume profiles, status history, and email logs.
"""

from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    location = Column(Text, default="Remote")
    stipend = Column(Text, default="Unpaid")
    required_skills = Column(Text, default="")
    job_description = Column(Text, default="")  # Full JD text from detail page
    deadline = Column(Text, default="N/A")
    link = Column(Text, default="")
    confidence_score = Column(Float, default=0.0)
    reputation_score = Column(Float, default=0.0)
    status = Column(String(50), default="New")
    date_added = Column(Date, default=date.today)
    source = Column(String(50), default="Unknown")
    job_hash = Column(String(64), unique=True, nullable=False)
    recruiter_email = Column(Text, default="")  # scraped or manually entered
    bookmarked = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)

    # Relationships
    status_history = relationship("JobStatusHistory", back_populates="job", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="job", cascade="all, delete-orphan")


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


class JobStatusHistory(Base):
    __tablename__ = "job_status_history"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    old_status = Column(String(50), default="")
    new_status = Column(String(50), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="status_history")


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    to_email = Column(Text, nullable=False)
    subject = Column(Text, default="")
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="sent")  # sent, failed

    job = relationship("Job", back_populates="email_logs")
