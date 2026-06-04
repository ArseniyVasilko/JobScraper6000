import bs4
from attr.filters import exclude


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

    return all_jobs