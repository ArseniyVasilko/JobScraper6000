import requests
from app.constants import ALL_JOB_PAGES
import time
import random

#To avoid bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

#Redirects to correct individual job board request method
def scan_all_jobs(job_board: str) -> list:
    if job_board == "Duunitori":
        return scan_duunitori()

#Scans 10 first pages of Duunitori IT industry job listings
def scan_duunitori() -> list:
    all_job_bodies = []
    for i in range(1, 11):
        response = requests.get(ALL_JOB_PAGES["Duunitori"] + str(i), headers=HEADERS, timeout=20)
        response.raise_for_status()
        all_job_bodies.append(response.text)
        time.sleep(random.uniform(3, 8))
    return all_job_bodies
