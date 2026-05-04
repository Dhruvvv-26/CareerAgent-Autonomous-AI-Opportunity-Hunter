
import os
import json
import logging
from sqlalchemy.orm import Session
from database.db import SessionLocal, init_db
from database.models import ResumeProfile, Job
from agents.resume_agent import parse_resume
from agents.search_agent import search_jobs
from agents.scoring_agent import score_jobs

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
logger = logging.getLogger("FullPipelineTest")

def run_test():
    logger.info("Starting Full Pipeline Integration Test")
    
    # 0. Initialize DB
    init_db()
    db = SessionLocal()
    
    try:
        # 1. Parse Resume
        resume_path = "resume.pdf"
        if not os.path.exists(resume_path):
            logger.error(f"Resume file not found at {resume_path}")
            return
            
        with open(resume_path, "rb") as f:
            file_bytes = f.read()
            
        logger.info("Step 1: Parsing Resume...")
        profile = parse_resume(file_bytes)
        logger.info(f"Detected Profile: {json.dumps(profile, indent=2)}")
        
        # Save profile to DB (simulating upload_resume logic)
        contact = profile.get("contact_info", {})
        existing = db.query(ResumeProfile).first()
        if existing:
            db.delete(existing) # Start fresh for test
        
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
            resume_file_path=os.path.abspath(resume_path),
        )
        db.add(db_profile)
        db.commit()
        
        # 2. Search Jobs
        logger.info("Step 2: Searching Jobs (including Unstop)...")
        # We'll pass the profile dict directly to search_jobs
        new_jobs = search_jobs(profile, db)
        logger.info(f"Search complete. Found {len(new_jobs)} new jobs.")
        
        # 3. Score Jobs
        logger.info("Step 3: Scoring Jobs...")
        scored_count = score_jobs(profile, db)
        logger.info(f"Scored {scored_count} jobs.")
        
        # 4. Analyze Results
        logger.info("Step 4: Analyzing Top Matches...")
        top_jobs = db.query(Job).order_by(Job.confidence_score.desc()).limit(5).all()
        
        print("\n" + "="*50)
        print("PIPELINE TEST RESULTS SUMMARY")
        print("="*50)
        print(f"Name: {profile['contact_info']['full_name']}")
        print(f"Top Skills: {', '.join(profile['skills'][:5])}")
        print(f"Preferred Roles: {', '.join(profile['preferred_roles'])}")
        print(f"Experience Level: {profile['experience_level']}")
        print("-"*50)
        print(f"Total Jobs in DB: {db.query(Job).count()}")
        print(f"New Jobs Found in this run: {len(new_jobs)}")
        print("-"*50)
        print("TOP 5 JOB MATCHES:")
        for i, job in enumerate(top_jobs):
            print(f"{i+1}. {job.role} at {job.company} ({job.source})")
            print(f"   Match Score: {job.confidence_score}% | Status: {job.status}")
            print(f"   Link: {job.link}")
            print("-" * 30)
        print("="*50)
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
