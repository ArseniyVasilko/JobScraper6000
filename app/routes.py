from app import app
from flask import render_template, request, session
from app.constants import ALL_JOB_PAGES
from app.services import ai_service, parsing_service, request_service
from flask import jsonify

@app.route('/')
def settings_panel():

    return render_template('settings_panel.html')

# For all job boards requested sends http request, parses http page,
# extracts the job listing links and connects to GeminiAPI to filter.
# Then saves results to the db and displays them on results_panel.html
@app.route('/get_results', methods=['GET'])
def get_results():
    filtered_jobs = {}
    for job_board in request.args.getlist('job_boards'):
        print("Requesting information for " + job_board)
        all_job_board_pages = request_service.scan_all_jobs(job_board)
        print(f"Http request for {job_board} successfully executed")
        all_job_details = parsing_service.scan_job_details(all_job_board_pages, job_board)
        print(f"Links successfully extracted")
        print(*all_job_details, sep="\n")
        filtered_job_links = ai_service.filter_with_ai(all_job_details)
        print(f"Job listings for {job_board} successfully filtered")
        print(filtered_job_links)
        filtered_jobs[job_board] = filtered_job_links
        print(job_board + "'s jobs appended to results")
    session["last_search_data"] = filtered_jobs
    # add_jobs_to_db(filtered_jobs)
    # print("All jobs successfully added to database")
    print(session["last_search_data"])
    return render_template('results_panel.html')

@app.route('/api/get_cards')
def get_cards():
    data = session.get('last_search_data', {})

    requested_boards = request.args.getlist('boards')
    requested_job_types = request.args.getlist('type') or ['filtered_jobs']
    requested_page = request.args.get('page', 1, type=int)
    per_page = 16

    selected_boards = {
        board_name: board_data
        for board_name, board_data in data.items()
        if not requested_boards or board_name in requested_boards
    }

    # Filters job listings based on requested job type (e.g. )
    cards = []
    for board, board_data in selected_boards.items():
        for job_group_type, jobs in board_data.items():
            if job_group_type in requested_job_types:
                for job in jobs:
                    job.update({"board": board, "status": job_group_type})
                    cards.append(job)

    start = (requested_page - 1) * per_page
    return jsonify({'cards': cards[start:start + per_page], 'has_more': start + per_page < len(cards)})




