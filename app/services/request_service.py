import requests
from app.constants import *
import time
import random

# Redirects to correct individual job board request method
def scan_all_jobs(job_board: str) -> list:
    if job_board == "Duunitori":
        return scan_duunitori()


# Fetches parsable page str from link
def fetch_page(page_link: str, headers=get_random_headers(), timeout=3, delay_min=3, delay_max=8) -> str:
    time.sleep(random.uniform(delay_min, delay_max))
    try:
        response = requests.get(page_link,
                                timeout=timeout,
                                headers=headers)
        response.raise_for_status()
        page = response.text
    except requests.RequestException as e:
        page = None
    return page


# Scans 10 first pages of Duunitori IT industry job listings
def scan_duunitori() -> list:
    all_job_bodies = []
    for i in range(1, DUUNITORI_MAX_PAGES + 1):
        response = fetch_page(page_link=ALL_JOB_PAGES["Duunitori"] + str(i), timeout=DUUNITORI_REQUEST_TIMEOUT)
        all_job_bodies.append(response)
    return all_job_bodies