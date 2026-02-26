"""
Daily Runner — APScheduler-based daily automation.
Runs search → scoring → email at the configured time (default 8 AM).
"""

import json
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from config import SCHEDULER_HOUR, SCHEDULER_MINUTE
from database.db import SessionLocal
from database.models import ResumeProfile
from agents.search_agent import search_jobs
from agents.scoring_agent import score_jobs
from agents.email_agent import send_cold_email

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _daily_job():
    """The daily automated pipeline: search → score → email."""
    logger.info("⏰ Daily automation started.")

    db = SessionLocal()
    try:
        # Get profile
        profile_row = db.query(ResumeProfile).first()
        if not profile_row:
            logger.warning("No resume profile found. Skipping daily run.")
            return

        profile = {
            "skills": json.loads(profile_row.skills),
            "domains": json.loads(profile_row.domains),
            "experience_level": profile_row.experience_level,
            "preferred_roles": json.loads(profile_row.preferred_roles),
        }

        # Step 1: Search
        new_jobs = search_jobs(profile, db)
        logger.info(f"Search found {len(new_jobs)} new jobs.")

        # Step 2: Score
        scored = score_jobs(profile, db)
        logger.info(f"Scored {scored} jobs.")

        # Step 3: Send 1 cold email
        result = send_cold_email(profile, db)
        logger.info(f"Email result: {result}")

    except Exception as e:
        logger.error(f"Daily automation error: {e}")
    finally:
        db.close()

    logger.info("✅ Daily automation complete.")


def start_scheduler():
    """Start the background scheduler for daily automation."""
    scheduler.add_job(
        _daily_job,
        "cron",
        hour=SCHEDULER_HOUR,
        minute=SCHEDULER_MINUTE,
        id="daily_career_agent",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started. Daily run at {SCHEDULER_HOUR:02d}:{SCHEDULER_MINUTE:02d}."
    )


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
