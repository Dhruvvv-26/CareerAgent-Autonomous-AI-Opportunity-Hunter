"""
Application configuration — loads from .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./career_agent.db")
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "token.json")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
SCHEDULER_HOUR = int(os.getenv("SCHEDULER_HOUR", "8"))
SCHEDULER_MINUTE = int(os.getenv("SCHEDULER_MINUTE", "0"))
