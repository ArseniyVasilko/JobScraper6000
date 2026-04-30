from app import app
from flask import render_template, request
from constants import ALL_JOB_PAGES
import requests
from app.services import ai_service, parsing_service, request_service

@app.route('/')
def settings_panel():

    return render_template('settings_panel.html')

# For all job boards requested sends http request, parses http page,
# extracts the job listing links and connects to GeminiAPI to filter.
# Then saves results to the db and displays them on results_panel.html
@app.route('/get_results', methods=['GET'])
def get_results():
    filtered_jobs = []
    for job_board in request.args.getlist('job_boards'):
        print("Requesting information for " + job_board)
        all_job_board_pages = request_logic.scan_all_jobs(job_board)
        print("Http request for " + job_board + "successfully executed")
        all_job_links = parsing_logic.scan_for_links(all_job_board_pages)
        print("Links successfully extracted")
        filtered_job_links = ai_logic.filter_with_ai(all_job_links)
        print("Jobs successfully filtered")
        filtered_jobs.append((job_board, filtered_job_links))
        print(job_board + "'s jobs appended to results")
    add_jobs_to_db(filtered_jobs)
    print("All jobs successfully added to database")
    return render_template('results_panel.html', filtered_jobs=filtered_jobs)

