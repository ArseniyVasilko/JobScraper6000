from app import app
from flask import render_template

@app.route('/')
def results_panel():

    return render_template('results_panel.html')


@app.route('/get_info', methods=['GET'])
def get_info():
    for job_board in request.args.getlist('job_boards'):
        print("Requesting information for " + job_board)
        