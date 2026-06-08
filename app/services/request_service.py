import requests
from app.constants import ALL_JOB_PAGES, DUUNITORI_MAX_PAGES, DUUNITORI_REQUEST_TIMEOUT, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX
import time
import random

#To avoid bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Connection": "keep-alive",
}


# Redirects to correct individual job board request method
def scan_all_jobs(job_board: str) -> list:
    if job_board == "Duunitori":
        return scan_duunitori()


# Fetches parsable page str from link
def fetch_page(page_link: str, headers=HEADERS, timeout=DUUNITORI_REQUEST_TIMEOUT) -> str:
    try:
        response = requests.get(page_link, timeout=timeout, headers=headers)
        response.raise_for_status()
        page = response.text
    except requests.RequestException as e:
        page = None
    return page


# Scans 10 first pages of Duunitori IT industry job listings
def scan_duunitori() -> list:
    all_job_bodies = []
    for i in range(1, DUUNITORI_MAX_PAGES + 1):
        response = fetch_page(page_link=ALL_JOB_PAGES["Duunitori"] + str(i), headers=HEADERS, timeout=DUUNITORI_REQUEST_TIMEOUT)
        all_job_bodies.append(response)
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
    return all_job_bodies