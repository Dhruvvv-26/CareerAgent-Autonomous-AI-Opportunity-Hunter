"""
Email Agent — sends personalized cold emails via Gmail API (OAuth Desktop).
Sends to the recruiter's email, includes your contact info, and attaches your resume PDF.
"""

import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allow HTTP for local dev
import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from config import GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH, SENDER_EMAIL
from database.models import Job, ResumeProfile

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _get_gmail_service():
    """Authenticate with Gmail API using OAuth desktop flow."""
    creds = None

    if os.path.exists(GMAIL_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(GMAIL_CREDENTIALS_PATH):
                logger.error(
                    f"credentials.json not found at {GMAIL_CREDENTIALS_PATH}. "
                    "Please download it from Google Cloud Console."
                )
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                GMAIL_CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(GMAIL_TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _get_contact_info(db: Session) -> dict:
    """Retrieve the user's contact info from the stored resume profile."""
    profile = db.query(ResumeProfile).first()
    if not profile:
        return {}
    return {
        "full_name": profile.full_name or "",
        "email": profile.email or SENDER_EMAIL,
        "phone": profile.phone or "",
        "linkedin_url": profile.linkedin_url or "",
        "github_url": profile.github_url or "",
        "resume_file_path": profile.resume_file_path or "",
    }


def generate_email_body(job: Job, profile: dict, contact: dict) -> str:
    """Generate a polished, professional cold email body."""
    skills = profile.get("skills", [])
    job_skills = [s.strip() for s in job.required_skills.split(",") if s.strip()]
    common = set(s.lower() for s in skills) & set(s.lower() for s in job_skills)

    # Pick the top 3–5 matching skills for a concise mention
    top_skills = sorted(common)[:5]
    skills_display = ", ".join(top_skills) if top_skills else "the core technologies listed in the role"

    name = contact.get("full_name", "").strip() or "Applicant"
    email = contact.get("email", "") or SENDER_EMAIL
    phone = contact.get("phone", "")
    linkedin = contact.get("linkedin_url", "")
    github = contact.get("github_url", "")

    # Determine experience-level phrasing
    exp = profile.get("experience_level", "Entry")
    if exp.lower() in ("senior", "mid"):
        exp_phrase = "an experienced professional"
    else:
        exp_phrase = "a motivated and detail-oriented candidate"

    # Build a clean signature block
    sig_lines = [name]
    if email:
        sig_lines.append(email)
    if phone:
        sig_lines.append(phone)
    if linkedin:
        sig_lines.append(linkedin)
    if github:
        sig_lines.append(github)
    signature = "\n".join(sig_lines)

    body = f"""Dear Hiring Team at {job.company},

I recently came across the {job.role} opening at {job.company} and was immediately drawn to the opportunity. As {exp_phrase} with demonstrated expertise in {skills_display}, I believe I can make a meaningful contribution to your team.

What I would bring to this role:

  • Hands-on proficiency in {skills_display}, directly aligned with the position's technical requirements
  • A track record of delivering production-quality work in collaborative, fast-paced environments
  • A genuine passion for continuous learning and building solutions that create real impact

I have attached my resume for your reference and would welcome the chance to discuss how my background and skills align with {job.company}'s goals.

Thank you for considering my application. I look forward to the opportunity to connect.

Warm regards,
{signature}
"""
    return body


def generate_email_subject(job: Job) -> str:
    """Generate a clean, professional subject line."""
    return f"Application: {job.role} — {job.company}"


def get_email_preview(job_id: int, profile: dict, db: Session) -> dict:
    """
    Generate an email preview for a specific job.
    Returns all email fields so the frontend can display & edit them.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"error": "Job not found."}

    contact = _get_contact_info(db)
    subject = generate_email_subject(job)
    body = generate_email_body(job, profile, contact)

    return {
        "job_id": job.id,
        "company": job.company,
        "role": job.role,
        "to": job.recruiter_email or "",
        "from": SENDER_EMAIL,
        "subject": subject,
        "body": body,
        "contact": contact,
        "has_resume": bool(contact.get("resume_file_path")),
    }


def send_cold_email(
    db: Session,
    profile: dict,
    job_id: int = None,
    to_email: str = None,
    subject: str = None,
    body: str = None,
) -> dict:
    """
    Send ONE personalized cold email.
    If job_id is provided, sends for that specific job.
    to_email, subject, body can override the auto-generated values (from preview edits).
    """
    # Find the job
    if job_id:
        job = db.query(Job).filter(Job.id == job_id).first()
    else:
        # Fallback: highest-priority unsent job
        job = (
            db.query(Job)
            .filter(Job.status.in_(["High Priority", "Good Match"]))
            .order_by(Job.confidence_score.desc())
            .first()
        )

    if not job:
        logger.info("No eligible jobs to email.")
        return {"status": "no_jobs", "message": "No eligible jobs found for emailing."}

    # Determine recipient
    recipient = to_email or job.recruiter_email
    if not recipient:
        return {
            "status": "no_email",
            "message": f"No recruiter email found for {job.company}. Please add one manually.",
        }

    # Get contact info and generate email content
    contact = _get_contact_info(db)
    final_subject = subject or generate_email_subject(job)
    final_body = body or generate_email_body(job, profile, contact)

    service = _get_gmail_service()
    if not service:
        return {"status": "auth_error", "message": "Gmail authentication failed."}

    # Build MIME message with attachment
    message = MIMEMultipart()
    message["to"] = recipient
    message["from"] = SENDER_EMAIL
    message["subject"] = final_subject

    # Attach body
    message.attach(MIMEText(final_body, "plain"))

    # Attach resume PDF if available
    resume_path = contact.get("resume_file_path", "")
    if resume_path and os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            pdf_data = f.read()
        attachment = MIMEApplication(pdf_data, _subtype="pdf")
        attachment.add_header(
            "Content-Disposition", "attachment",
            filename=f"{contact.get('full_name', 'Resume').replace(' ', '_')}_Resume.pdf"
        )
        message.attach(attachment)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()

        job.status = "Emailed"
        db.commit()

        logger.info(f"Email sent for: {job.role} at {job.company} → {recipient}")
        return {
            "status": "sent",
            "company": job.company,
            "role": job.role,
            "to": recipient,
            "subject": final_subject,
        }
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return {"status": "error", "message": str(e)}
