import bs4
from app.constants import *
from concurrent import futures
import app.services.request_service as request_service


def scan_job_details(all_job_board_pages: list, job_board: str) -> list:
    if job_board == "Duunitori":
        return scan_duunitori(all_job_board_pages)


def scan_duunitori(all_job_board_pages):
    all_jobs = []

    for page in all_job_board_pages:
        page_tree = bs4.BeautifulSoup(page, 'html.parser')

        # Locate the "Duunitori suosittelee" sponsored section to exclude it
        exclude_text = page_tree.find(string=lambda t: t and "Duunitori suosittelee" in t)
        exclude_container = (
            exclude_text.parent.parent.parent if exclude_text else None
        )

        # Extract data from job cards on the page
        page_jobs = [
            {
                "link":     "https://duunitori.fi" + card.find("a", class_=["job-box__hover", "gtm-search-result"]).get("href"),
                "title":    card.find("h3", class_="job-box__title").get_text(strip=True),
                "location": card.find("span", class_="job-box__job-location").get_text(strip=True).rstrip(" –"),
                "date":     card.find("span", class_="job-box__job-posted").get_text(strip=True),
            }
            for card in page_tree.find_all("div", class_="job-box")
            if card.find("a", class_=["job-box__hover", "gtm-search-result"])
            and card.find("h3", class_="job-box__title")
            and (exclude_container is None or exclude_container not in card.parents)
        ]
        all_jobs.extend(page_jobs)
        print("all jobs test:", all_jobs)

    if MAX_JOBS_PARSED_DUUNITORI:
        all_jobs = all_jobs[:MAX_JOBS_PARSED_DUUNITORI]
    # Asynchronously fetch individual job listing pages and extract+add text descriptions to each job's dict
    with futures.ThreadPoolExecutor(max_workers=DUUNITORI_MAX_WORKERS) as executor:
        def fetch_and_assign(job):
            job["text"] = (bs4
                            .BeautifulSoup(request_service
                                           .fetch_page(job["link"],
                                                       delay_min=DUUNITORI_REQUEST_DELAY_MIN,
                                                       delay_max=DUUNITORI_REQUEST_DELAY_MAX,
                                                       timeout=DUUNITORI_REQUEST_TIMEOUT
                                                       ),
                                                'html.parser')
                            .find("div", class_="description--jobentry")
                            .get_text(separator=" ", strip=True))
            return job
        all_jobs = list(executor.map(fetch_and_assign, all_jobs))
    return all_jobs