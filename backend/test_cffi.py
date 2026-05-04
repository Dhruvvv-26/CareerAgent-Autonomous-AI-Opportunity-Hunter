import logging
from curl_cffi import requests
from bs4 import BeautifulSoup

url = "https://www.indeed.com/jobs?q=software+intern&l=India"

try:
    resp = requests.get(url, impersonate="chrome120", timeout=15)
    print(f"Indeed HTTP {resp.status_code}")
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select(".job_seen_beacon, .resultContent, .tapItem, .result")
    print(f"Indeed found {len(cards)} listings")
except Exception as e:
    print(f"Indeed error: {e}")

url_wf = "https://wellfound.com/role/r/software-intern"
try:
    resp = requests.get(url_wf, impersonate="chrome120", timeout=15)
    print(f"Wellfound HTTP {resp.status_code}")
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("[data-test='StartupResult'], .styles_result__rPRNG, .styles_component__FLWLJ")
    print(f"Wellfound found {len(cards)} listings")
except Exception as e:
    print(f"Wellfound error: {e}")
