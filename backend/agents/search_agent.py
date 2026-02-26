"""
Search Agent — scrapes job listings from 7 portals:
  Internshala, Wellfound, Indeed, LinkedIn, Naukri, Glassdoor, SimplyHired.
Uses requests + BeautifulSoup. Generates SHA256 hash for deduplication.
"""

import hashlib
import logging
from datetime import date
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from database.models import Job

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 15


def _generate_hash(company: str, role: str, link: str) -> str:
    """Generate a unique SHA256 hash for deduplication."""
    raw = f"{company.strip().lower()}|{role.strip().lower()}|{link.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _job_exists(db: Session, job_hash: str) -> bool:
    """Check if a job with this hash already exists in the database."""
    return db.query(Job).filter(Job.job_hash == job_hash).first() is not None


# ---------------------------------------------------------------------------
# 1. Internshala scraper
# ---------------------------------------------------------------------------
def _scrape_internshala(keywords: list[str]) -> list[dict]:
    """Scrape internships from Internshala."""
    jobs = []
    query = "-".join(keywords[:3])
    url = f"https://internshala.com/internships/{query}-internship"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        listings = soup.select(".individual_internship, .internship_meta, .container-fluid.individual_internship")[:15]
        for listing in listings:
            try:
                company_tag = listing.select_one(".company_name a, .company_name, .link_display_like_text")
                role_tag = listing.select_one(".job-internship-name a, h3.job-internship-name, .profile a")
                location_tag = listing.select_one("#location_names span, .location_link a, a.location_link")
                stipend_tag = listing.select_one(".stipend, span.desktop-text, .stipend_container_table_cell .desktop-text")
                link_tag = listing.select_one("a.view_detail_button, .job-internship-name a, .profile a")

                company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                role = role_tag.get_text(strip=True) if role_tag else "Internship"
                location = location_tag.get_text(strip=True) if location_tag else "Remote"
                stipend = stipend_tag.get_text(strip=True) if stipend_tag else "Unpaid"

                link = ""
                if link_tag and link_tag.get("href"):
                    href = link_tag["href"]
                    link = href if href.startswith("http") else f"https://internshala.com{href}"

                jobs.append({
                    "company": company,
                    "role": role,
                    "location": location,
                    "stipend": stipend,
                    "required_skills": ", ".join(keywords),
                    "deadline": "N/A",
                    "link": link,
                    "source": "Internshala",
                })
            except Exception as e:
                logger.debug(f"Internshala listing parse error: {e}")
                continue
    except Exception as e:
        logger.warning(f"Internshala scrape failed: {e}")

    return jobs


# ---------------------------------------------------------------------------
# 2. Wellfound (AngelList) scraper
# ---------------------------------------------------------------------------
def _scrape_wellfound(keywords: list[str]) -> list[dict]:
    """Scrape jobs from Wellfound (formerly AngelList)."""
    jobs = []
    query = "-".join(keywords[:3])
    url = f"https://wellfound.com/role/r/{query}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        listings = soup.select("[data-test='StartupResult'], .styles_result__rPRNG, .styles_component__FLWLJ")[:15]
        for listing in listings:
            try:
                company_tag = listing.select_one("h2, .styles_name__Hnkhq, .styles_component__FLWLJ h2")
                role_tag = listing.select_one(".styles_title__xpQDw, a[class*='title'], .styles_listingTitle__RP2o1")
                location_tag = listing.select_one(".styles_location__Ej2hq, span[class*='location']")
                salary_tag = listing.select_one(".styles_compensation__MN_Ze, span[class*='compensation']")

                company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                role = role_tag.get_text(strip=True) if role_tag else "Role"
                location = location_tag.get_text(strip=True) if location_tag else "Remote"
                stipend = salary_tag.get_text(strip=True) if salary_tag else "Not disclosed"

                link_tag = listing.select_one("a[href]")
                link = ""
                if link_tag and link_tag.get("href"):
                    href = link_tag["href"]
                    link = href if href.startswith("http") else f"https://wellfound.com{href}"

                jobs.append({
                    "company": company,
                    "role": role,
                    "location": location,
                    "stipend": stipend,
                    "required_skills": ", ".join(keywords),
                    "deadline": "N/A",
                    "link": link,
                    "source": "Wellfound",
                })
            except Exception as e:
                logger.debug(f"Wellfound listing parse error: {e}")
                continue
    except Exception as e:
        logger.warning(f"Wellfound scrape failed: {e}")

    return jobs


# ---------------------------------------------------------------------------
# 3. Indeed scraper
# ---------------------------------------------------------------------------
def _scrape_indeed(keywords: list[str]) -> list[dict]:
    """Scrape jobs from Indeed basic search."""
    jobs = []
    query = "+".join(keywords[:3])
    url = f"https://www.indeed.com/jobs?q={query}&l=India"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.select(".job_seen_beacon, .resultContent, .tapItem, .result")[:15]
        for card in cards:
            try:
                title_tag = card.select_one("h2.jobTitle span, .jobTitle a span, h2.jobTitle a")
                company_tag = card.select_one("[data-testid='company-name'], .companyName, span.css-92r8pb")
                location_tag = card.select_one("[data-testid='text-location'], .companyLocation, div.css-1p0sjhy")
                salary_tag = card.select_one(".salary-snippet-container, .metadata.salary-snippet-container, .estimated-salary")
                link_tag = card.select_one("a[href]")

                role = title_tag.get_text(strip=True) if title_tag else "Role"
                company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                location = location_tag.get_text(strip=True) if location_tag else "India"
                stipend = salary_tag.get_text(strip=True) if salary_tag else "Not disclosed"

                link = ""
                if link_tag and link_tag.get("href"):
                    href = link_tag["href"]
                    link = href if href.startswith("http") else f"https://www.indeed.com{href}"

                jobs.append({
                    "company": company,
                    "role": role,
                    "location": location,
                    "stipend": stipend,
                    "required_skills": ", ".join(keywords),
                    "deadline": "N/A",
                    "link": link,
                    "source": "Indeed",
                })
            except Exception as e:
                logger.debug(f"Indeed listing parse error: {e}")
                continue
    except Exception as e:
        logger.warning(f"Indeed scrape failed: {e}")

    return jobs


# ---------------------------------------------------------------------------
# 4. LinkedIn Jobs scraper
# ---------------------------------------------------------------------------
def _scrape_linkedin(keywords: list[str]) -> list[dict]:
    """Scrape jobs from LinkedIn Jobs public search (no login required)."""
    jobs = []
    query = quote_plus(" ".join(keywords[:3]))
    url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location=India&f_TPR=r2592000"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.select(".base-card, .job-search-card, .base-search-card")[:15]
        for card in cards:
            try:
                title_tag = card.select_one(".base-search-card__title, h3.base-search-card__title")
                company_tag = card.select_one(".base-search-card__subtitle a, h4.base-search-card__subtitle")
                location_tag = card.select_one(".job-search-card__location, .base-search-card__metadata span")
                link_tag = card.select_one("a.base-card__full-link, a[href*='linkedin.com/jobs']")

                role = title_tag.get_text(strip=True) if title_tag else "Role"
                company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                location = location_tag.get_text(strip=True) if location_tag else "India"

                link = ""
                if link_tag and link_tag.get("href"):
                    link = link_tag["href"].split("?")[0]

                jobs.append({
                    "company": company,
                    "role": role,
                    "location": location,
                    "stipend": "Not disclosed",
                    "required_skills": ", ".join(keywords),
                    "deadline": "N/A",
                    "link": link,
                    "source": "LinkedIn",
                })
            except Exception as e:
                logger.debug(f"LinkedIn listing parse error: {e}")
                continue
    except Exception as e:
        logger.warning(f"LinkedIn scrape failed: {e}")

    return jobs


# ---------------------------------------------------------------------------
# 5. Naukri.com scraper
# ---------------------------------------------------------------------------
def _scrape_naukri(keywords: list[str]) -> list[dict]:
    """Scrape jobs from Naukri.com."""
    jobs = []
    query = "-".join(keywords[:3])
    url = f"https://www.naukri.com/{query}-jobs"

    naukri_headers = {**HEADERS, "Accept-Language": "en-US,en;q=0.9"}

    try:
        resp = requests.get(url, headers=naukri_headers, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.select(".srp-jobtuple-wrapper, article.jobTuple, .jobTupleHeader, .cust-job-tuple")[:15]
        for card in cards:
            try:
                title_tag = card.select_one(".title, a.title, .info-container .row1 a")
                company_tag = card.select_one(".comp-name, a.subTitle, .info-container .row2 a")
                location_tag = card.select_one(".loc-wrap .loc, .locWrap .ellipsis, .info-container .row3 .loc")
                salary_tag = card.select_one(".sal-wrap .ni-job-tuple-icon + span, .info-container .row3 .sal")

                role = title_tag.get_text(strip=True) if title_tag else "Role"
                company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                location = location_tag.get_text(strip=True) if location_tag else "India"
                stipend = salary_tag.get_text(strip=True) if salary_tag else "Not disclosed"

                link_tag = card.select_one("a.title, a[href*='naukri.com']")
                link = ""
                if link_tag and link_tag.get("href"):
                    link = link_tag["href"]

                jobs.append({
                    "company": company,
                    "role": role,
                    "location": location,
                    "stipend": stipend,
                    "required_skills": ", ".join(keywords),
                    "deadline": "N/A",
                    "link": link,
                    "source": "Naukri",
                })
            except Exception as e:
                logger.debug(f"Naukri listing parse error: {e}")
                continue
    except Exception as e:
        logger.warning(f"Naukri scrape failed: {e}")

    return jobs


# ---------------------------------------------------------------------------
# 6. Glassdoor scraper
# ---------------------------------------------------------------------------
def _scrape_glassdoor(keywords: list[str]) -> list[dict]:
    """Scrape jobs from Glassdoor."""
    jobs = []
    query = quote_plus(" ".join(keywords[:3]))
    url = f"https://www.glassdoor.co.in/Job/india-{'-'.join(keywords[:3])}-jobs-SRCH_IL.0,5_IN115_KO6,{6+len('-'.join(keywords[:3]))}.htm"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.select(".react-job-listing, li[data-test='jobListing'], .JobCard_jobCardContainer__arkaK")[:15]
        for card in cards:
            try:
                title_tag = card.select_one(".job-title, a[data-test='job-link'], .JobCard_jobTitle__GLyJ1")
                company_tag = card.select_one(".employer-name, .EmployerProfile_compactEmployerName__LE242, .JobCard_companyName__N1YSU")
                location_tag = card.select_one(".job-location, .location, .JobCard_location__rCz3x")
                salary_tag = card.select_one(".salary-estimate, .JobCard_salaryEstimate__arV5J")

                role = title_tag.get_text(strip=True) if title_tag else "Role"
                company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                location = location_tag.get_text(strip=True) if location_tag else "India"
                stipend = salary_tag.get_text(strip=True) if salary_tag else "Not disclosed"

                link_tag = card.select_one("a[href]")
                link = ""
                if link_tag and link_tag.get("href"):
                    href = link_tag["href"]
                    link = href if href.startswith("http") else f"https://www.glassdoor.co.in{href}"

                jobs.append({
                    "company": company,
                    "role": role,
                    "location": location,
                    "stipend": stipend,
                    "required_skills": ", ".join(keywords),
                    "deadline": "N/A",
                    "link": link,
                    "source": "Glassdoor",
                })
            except Exception as e:
                logger.debug(f"Glassdoor listing parse error: {e}")
                continue
    except Exception as e:
        logger.warning(f"Glassdoor scrape failed: {e}")

    return jobs


# ---------------------------------------------------------------------------
# 7. SimplyHired scraper
# ---------------------------------------------------------------------------
def _scrape_simplyhired(keywords: list[str]) -> list[dict]:
    """Scrape jobs from SimplyHired."""
    jobs = []
    query = quote_plus(" ".join(keywords[:3]))
    url = f"https://www.simplyhired.co.in/search?q={query}&l=India"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.select(".SerpJob, article[data-testid='searchSerpJob'], .css-0")[:15]
        for card in cards:
            try:
                title_tag = card.select_one("h2 a, a[data-testid='searchSerpJobTitle'], .SerpJob-title a")
                company_tag = card.select_one("[data-testid='companyName'], .SerpJob-metaInfo span:first-child, .jobposting-company")
                location_tag = card.select_one("[data-testid='searchSerpJobLocation'], .SerpJob-metaInfoLocation span, .jobposting-location")
                salary_tag = card.select_one("[data-testid='searchSerpJobSalaryEst'], .SerpJob-metaInfoSalary, .jobposting-salary")

                role = title_tag.get_text(strip=True) if title_tag else "Role"
                company = company_tag.get_text(strip=True) if company_tag else "Unknown"
                location = location_tag.get_text(strip=True) if location_tag else "India"
                stipend = salary_tag.get_text(strip=True) if salary_tag else "Not disclosed"

                link_tag = card.select_one("a[href]")
                link = ""
                if link_tag and link_tag.get("href"):
                    href = link_tag["href"]
                    link = href if href.startswith("http") else f"https://www.simplyhired.co.in{href}"

                jobs.append({
                    "company": company,
                    "role": role,
                    "location": location,
                    "stipend": stipend,
                    "required_skills": ", ".join(keywords),
                    "deadline": "N/A",
                    "link": link,
                    "source": "SimplyHired",
                })
            except Exception as e:
                logger.debug(f"SimplyHired listing parse error: {e}")
                continue
    except Exception as e:
        logger.warning(f"SimplyHired scrape failed: {e}")

    return jobs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def search_jobs(profile: dict, db: Session) -> list[dict]:
    """
    Search all 7 sources for jobs matching the user's profile.
    Deduplicates against the database. Returns newly added jobs.
    """
    keywords = profile.get("skills", [])[:5]
    if not keywords:
        keywords = profile.get("preferred_roles", ["software engineer"])

    all_raw: list[dict] = []

    # Scrape all portals (each wrapped in try/except internally)
    scrapers = [
        ("Internshala", _scrape_internshala),
        ("Wellfound", _scrape_wellfound),
        ("Indeed", _scrape_indeed),
        ("LinkedIn", _scrape_linkedin),
        ("Naukri", _scrape_naukri),
        ("Glassdoor", _scrape_glassdoor),
        ("SimplyHired", _scrape_simplyhired),
    ]

    for name, scraper_fn in scrapers:
        try:
            results = scraper_fn(keywords)
            logger.info(f"{name}: found {len(results)} listings")
            all_raw.extend(results)
        except Exception as e:
            logger.warning(f"{name} scraper crashed: {e}")

    new_jobs = []
    seen_hashes = set()
    for raw in all_raw:
        job_hash = _generate_hash(raw["company"], raw["role"], raw.get("link", ""))
        if job_hash in seen_hashes:
            continue
        seen_hashes.add(job_hash)
        if _job_exists(db, job_hash):
            continue

        job = Job(
            company=raw["company"],
            role=raw["role"],
            location=raw["location"],
            stipend=raw["stipend"],
            required_skills=raw["required_skills"],
            deadline=raw.get("deadline", "N/A"),
            link=raw.get("link", ""),
            confidence_score=0.0,
            reputation_score=0.0,
            status="New",
            date_added=date.today(),
            source=raw.get("source", "Unknown"),
            job_hash=job_hash,
        )
        db.add(job)
        new_jobs.append(raw)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"DB commit error: {e}")
    logger.info(f"Search complete: {len(new_jobs)} new jobs added out of {len(all_raw)} found.")
    return new_jobs
