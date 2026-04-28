from app import app
from flask import render_template
from all_jobs import ALL_JOB_PAGES
import requests

@app.route('/')
def results_panel():

    return render_template('results_panel.html')


@app.route('/get_results', methods=['GET'])
def get_results():
    filtered_jobs = []
    for job_board in request.args.getlist('job_boards'):
        print("Requesting information for " + job_board)
        all_job_board_pages = scan_all_jobs(job_board)
        all_job_links = scan_for_links(all_job_board_pages)
        filtered_job_links = filter_with_ai(all_job_links)
        filtered_jobs.append((job_board, filtered_job_links))
    add_jobs_to_db(filtered_jobs)
    return render_template('results_panel.html', filtered_jobs=filtered_jobs)
        # page_info = requests.get(ALL_JOB_PAGES[job_board])
        # page_info = BeautifulSoup(page_info.content, 'html.parser')
        # return page_info
