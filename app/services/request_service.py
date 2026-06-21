import requests
from app.constants import *
import time
import random

# Redirects to correct individual job board request method
def scan_all_jobs(job_board: str) -> list:
    if job_board == "Duunitori":
        return scan_duunitori()


# Fetches parsable page str from link
def fetch_page(page_link: str, headers=None, timeout=3, delay_min=3, delay_max=8) -> str:
    headers = headers or get_random_headers()
    time.sleep(random.uniform(delay_min, delay_max))
    print("Fetching " + page_link)
    try:
        response = requests.get(page_link,
                                timeout=timeout,
                                headers=headers)
        response.raise_for_status()
        page = response.text
        print("Page scraped successfully with headers: ", headers)
    except requests.RequestException as e:
        print(f"Error fetching page {page_link}: {e}")
        page = None
    return page


# Scans DUUNITORI_MAX_PAGES first pages of Duunitori IT industry job listings
def scan_duunitori() -> list:
    all_job_bodies = []
    for i in range(1, DUUNITORI_MAX_PAGES + 1):
        print("Fetching page:", ALL_JOB_PAGES["Duunitori"] + str(i))
        response = fetch_page(page_link=ALL_JOB_PAGES["Duunitori"] + str(i), timeout=DUUNITORI_REQUEST_TIMEOUT)
        all_job_bodies.append(response)
    return all_job_bodies