import sys
import logging
from agents.search_agent import (
    _scrape_internshala, _scrape_wellfound, _scrape_indeed, 
    _scrape_linkedin, _scrape_naukri, _scrape_glassdoor, _scrape_simplyhired
)

logging.basicConfig(level=logging.DEBUG)

keywords = ["software", "intern"]

print("Testing Internshala:", len(_scrape_internshala(keywords)))
print("Testing Wellfound:", len(_scrape_wellfound(keywords)))
print("Testing Indeed:", len(_scrape_indeed(keywords)))
print("Testing LinkedIn:", len(_scrape_linkedin(keywords)))
print("Testing Naukri:", len(_scrape_naukri(keywords)))
print("Testing Glassdoor:", len(_scrape_glassdoor(keywords)))
print("Testing SimplyHired:", len(_scrape_simplyhired(keywords)))
