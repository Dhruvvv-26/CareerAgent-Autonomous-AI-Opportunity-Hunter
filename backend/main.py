"""
CareerAgent — FastAPI Application Entry Point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db
from routers import resume_router, jobs_router
from scheduler.daily_runner import start_scheduler, stop_scheduler

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan events
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("🚀 Starting CareerAgent backend…")
    init_db()
    start_scheduler()
    yield
    stop_scheduler()
    logger.info("CareerAgent backend shut down.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="CareerAgent API",
    description="Autonomous AI Opportunity Hunter",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router.router, tags=["Resume"])
app.include_router(jobs_router.router, tags=["Jobs"])


@app.get("/")
def root():
    return {"message": "CareerAgent API is running."}
