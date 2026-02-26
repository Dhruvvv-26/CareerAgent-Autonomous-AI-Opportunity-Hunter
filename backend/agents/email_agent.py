"""
Email Agent — sends one personalized cold email daily via Gmail API (OAuth Desktop).
"""

import os
import base64
import logging
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from config import GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH, SENDER_EMAIL
from database.models import Job

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


def _generate_email_body(job: Job, profile: dict) -> str:
    """Generate a personalized cold email body."""
    skills = profile.get("skills", [])
    job_skills = [s.strip() for s in job.required_skills.split(",") if s.strip()]
    common = set(s.lower() for s in skills) & set(s.lower() for s in job_skills)
    common_display = ", ".join(sorted(common)) if common else "relevant technical skills"

    body = f"""Dear Hiring Manager at {job.company},

I am writing to express my strong interest in the {job.role} position at {job.company}. After reviewing the role requirements, I am confident that my background aligns well with what you are looking for.

I bring hands-on experience in {common_display}, which directly maps to the technical requirements of this role. My recent projects demonstrate practical application of these skills in solving real-world problems.

Key highlights:
• Strong proficiency in {common_display}
• Proven ability to deliver results in fast-paced environments
• Passionate about continuous learning and contributing to impactful teams

I would love the opportunity to discuss how my skills and enthusiasm can contribute to {job.company}'s mission. Please find my portfolio and work at [GitHub Profile].

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
[Your Name]
{SENDER_EMAIL}
"""
    return body


def send_cold_email(profile: dict, db: Session) -> dict:
    """
    Send ONE personalized cold email for the highest-priority unsent job.
    Returns status dict.
    """
    # Find the best unsent job (highest confidence, not already emailed)
    job = (
        db.query(Job)
        .filter(Job.status.in_(["High Priority", "Good Match"]))
        .order_by(Job.confidence_score.desc())
        .first()
    )

    if not job:
        logger.info("No eligible jobs to email.")
        return {"status": "no_jobs", "message": "No eligible jobs found for emailing."}

    service = _get_gmail_service()
    if not service:
        return {"status": "auth_error", "message": "Gmail authentication failed."}

    subject = f"Application for {job.role} – AI/ML Enthusiast"
    body = _generate_email_body(job, profile)

    message = MIMEText(body)
    message["to"] = SENDER_EMAIL  # placeholder — in production, use HR email
    message["from"] = SENDER_EMAIL
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()

        job.status = "Emailed"
        db.commit()

        logger.info(f"Email sent for: {job.role} at {job.company}")
        return {
            "status": "sent",
            "company": job.company,
            "role": job.role,
            "subject": subject,
        }
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return {"status": "error", "message": str(e)}
