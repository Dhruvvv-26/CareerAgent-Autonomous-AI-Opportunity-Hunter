# 🚀 CareerAgent — Autonomous AI Opportunity Hunter

> A multi-agent AI system that autonomously discovers job opportunities across 7 portals, matches them against your resume using **TF-IDF intelligence**, scores and categorizes them, tracks your application history, and sends personalized cold emails — all running **100% locally** with **zero paid APIs**.

**Built by [Dhruv Gupta](https://github.com/Dhruvvv-26)**

---

## ✨ Features

- **Multi-Portal Job Scraping** — Searches 7 portals with retry logic & exponential backoff, extracts real job descriptions and recruiter/HR emails
- **Resume Intelligence** — Extracts skills, domains, and contact info (phone/email/LinkedIn) from your PDF resume
- **TF-IDF Smart Scoring** — Computes confidence scores using TF-IDF + cosine similarity for fuzzy skill matching, with synonym normalization
- **Interactive Email Outreach** — Generate, preview, edit, and send polished cold emails with a single click; full email send history logging
- **Auto Categorization** — Jobs classified into High Priority, Good Match, and Stretch tiers
- **Daily Automation** — APScheduler runs the full pipeline on a configurable daily schedule
- **Gmail API Integration** — Dispatches cold emails with your custom resume attached via OAuth Desktop
- **Premium Dark Dashboard** — Clean, minimal React frontend with filters, search, and status tracking
- **📊 Analytics Dashboard** — Interactive pie, bar, and line charts (Recharts) for source distribution, category breakdown, and daily trends
- **⭐ Bookmarks & Favorites** — Star important jobs for quick access with a dedicated filter
- **📥 CSV Export** — Export your entire job list as a downloadable CSV file
- **🗑️ Archive & Delete** — Soft-delete jobs to keep your dashboard clean, restore anytime
- **📋 Application Tracker** — Full status change history with timeline view per job
- **📨 Email History** — Track every cold email sent with recipient, subject, and timestamp
- **🔄 Pagination** — Server-side pagination for handling large job listings
- **💾 Persistent Profile** — Resume summary persists across page refreshes

---

## 🏗 Architecture

```
React + Vite Frontend  →  FastAPI Backend  →  Multi-Agent Layer  →  SQLite  →  Gmail API (OAuth)
```

### Agent System

| Agent | Responsibility |
|-------|---------------|
| **Resume Agent** | Parses PDF resumes, extracts skills, domains, experience level |
| **Search Agent** | Scrapes 7 job portals with deduplication via SHA-256 hashing, retry logic, and real JD extraction |
| **Scoring Agent** | Computes confidence + reputation scores using TF-IDF matching, categorizes jobs |
| **Email Agent** | Sends personalized cold emails via Gmail API (1/day) |

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------| 
| Frontend | React, Vite, Axios, Recharts, Plain CSS |
| Backend | FastAPI, Uvicorn, SQLAlchemy |
| Scraping | Requests, BeautifulSoup4 (with retry/backoff) |
| Database | SQLite |
| NLP | PyMuPDF, scikit-learn (TF-IDF), Keyword Matching |
| Email | Gmail API (OAuth 2.0 Desktop) |
| Scheduling | APScheduler |

---

## 🔧 Setup

### Prerequisites

- Python 3.10+
- Node.js 18+ & npm
- Google Cloud project with Gmail API enabled (free tier)

### 1. Clone & Navigate

```bash
git clone https://github.com/Dhruvvv-26/CareerAgent.git
cd CareerAgent
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Gmail API** from the API Library
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Application type: **Desktop App**
6. Download the JSON and save it as `backend/credentials.json`
7. Add your email to **Test users** under the OAuth consent screen

> The first time the email agent runs, a browser window will open for OAuth consent. After that, `token.json` is cached locally.

### 4. Configure Environment

Edit `backend/.env`:

```env
DATABASE_URL=sqlite:///./career_agent.db
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
SENDER_EMAIL=your_email@gmail.com
SCHEDULER_HOUR=8
SCHEDULER_MINUTE=0
```

### 5. Frontend Setup

```bash
cd frontend
npm install
```

---

## 🚀 Running

### Start Backend

```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Start Frontend

```bash
cd frontend
npm run dev
```

Open: [http://localhost:5173](http://localhost:5173)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload-resume` | Upload PDF resume, extract skills and profile |
| `POST` | `/run-search` | Trigger job search + scoring pipeline across 7 portals |
| `GET` | `/jobs` | List jobs (supports `?category=`, `?page=`, `?per_page=`, `?bookmarked=`) |
| `GET` | `/job-stats` | Aggregate counts by category, source, and daily trend |
| `GET` | `/profile` | Retrieve current resume profile |
| `PUT` | `/update-status/{job_id}` | Update job status (records in history) |
| `PUT` | `/update-recruiter-email/{job_id}` | Manually set recruiter email |
| `PUT` | `/toggle-bookmark/{job_id}` | Toggle bookmark on a job |
| `PUT` | `/archive-job/{job_id}` | Archive/restore a job |
| `DELETE` | `/delete-job/{job_id}` | Permanently delete a job |
| `GET` | `/status-history/{job_id}` | Get status change timeline |
| `GET` | `/email-history/{job_id}` | Get email send history |
| `GET` | `/export-jobs` | Download all jobs as CSV |
| `GET` | `/email-preview/{job_id}` | Generate email preview for editing |
| `POST` | `/send-email` | Send cold email with optional overrides |

---

## 📊 Scoring System

| Metric | Formula |
|--------|---------|
| **Skill Match** | TF-IDF cosine similarity (60%) + exact keyword match (40%) |
| **Confidence** | `0.5 × skill_match + 0.3 × domain_match + 0.2 × experience_match` |
| **Reputation** | IIT/ISRO/FAANG = 95, MNC = 85, Funded Startup = 75, Unknown = 60 |

### Categories

| Category | Confidence Range |
|----------|-----------------| 
| 🟢 High Priority | > 80% |
| 🔵 Good Match | 60–80% |
| 🟡 Stretch | < 60% |

---

## ⏰ Scheduler

The backend runs an **APScheduler** background job:

- **Default**: Daily at 8:00 AM
- **Pipeline**: Search → Score → Send 1 cold email
- Configure via `.env` (`SCHEDULER_HOUR`, `SCHEDULER_MINUTE`)

---

## 📁 Project Structure

```
career_agent/
├── backend/
│   ├── main.py                      # FastAPI entry point + lifespan
│   ├── config.py                    # Environment configuration
│   ├── requirements.txt
│   ├── agents/
│   │   ├── resume_agent.py          # PDF parsing + skill extraction
│   │   ├── search_agent.py          # 7-portal web scraping + retry + JD extraction
│   │   ├── scoring_agent.py         # TF-IDF scoring + categorization
│   │   └── email_agent.py           # Gmail cold email sender
│   ├── database/
│   │   ├── db.py                    # SQLAlchemy engine + session
│   │   └── models.py               # Job, ResumeProfile, StatusHistory, EmailLog
│   ├── routers/
│   │   ├── resume_router.py         # /upload-resume endpoint
│   │   └── jobs_router.py           # All job, analytics, export, bookmark endpoints
│   ├── utils/
│   │   ├── skill_matcher.py         # TF-IDF + cosine similarity matcher
│   │   ├── reputation_score.py      # Company reputation scorer
│   │   └── confidence_calculator.py # Weighted confidence formula
│   └── scheduler/
│       └── daily_runner.py          # APScheduler daily automation
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx                  # Page composition
│       ├── main.jsx                 # Entry point
│       ├── index.css                # Complete design system
│       ├── api/
│       │   └── api.js               # Axios API wrapper (all endpoints)
│       ├── components/
│           ├── Navbar.jsx           # Top navigation bar
│           ├── ResumeUpload.jsx     # Upload + drag & drop + persistent profile
│           ├── ResumeSummaryCard.jsx # Skills, domains, experience
│           ├── Dashboard.jsx        # Dashboard container + pagination + export
│           ├── AnalyticsPanel.jsx   # Charts (pie, bar, line) with Recharts
│           ├── CategoryTabs.jsx     # Category filter tabs
│           ├── FilterBar.jsx        # Dropdown + search
│           ├── JobTable.jsx         # Job listing table
│           ├── JobRow.jsx           # Job row + bookmark + archive + history
│           ├── Pagination.jsx       # Page navigator
│           ├── StatusBadge.jsx      # Colored status badges
│           ├── EmailPreviewModal.jsx # Editable email composer modal
│           └── EmptyState.jsx       # Empty state UI
├── .gitignore
└── README.md
```

---

## 🔒 Security

- All secrets in `.env` (gitignored)
- `credentials.json` and `token.json` are gitignored
- No hardcoded API keys or secrets
- OAuth tokens stored locally only
- CORS restricted to localhost origins
- SQLite database gitignored

---

## 📜 License

This project is for personal/educational use. 100% free, 100% local.

---

**Made by [Dhruv Gupta](https://github.com/Dhruvvv-26)** 🚀
