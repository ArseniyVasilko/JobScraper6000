import bs4

def scan_for_links(all_job_board_pages: list, job_board: str) -> list:
    if job_board == "Duunitori":
        return scan_duunitori(all_job_board_pages)

def scan_duunitori(all_job_board_pages):
    all_job_links = []

    for page in all_job_board_pages:
        page_tree = bs4.BeautifulSoup(page, 'html.parser')
        job_link_tags = page_tree.find_all("a", class_=["job-box__hover", "gtm-search-result"])
        for tag in job_link_tags:
            all_job_links.append("https://duunitori.fi" + tag.get("href"))
    return all_job_links