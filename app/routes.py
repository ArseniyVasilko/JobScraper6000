from app import app
from flask import render_template

@app.route('/')
def results_panel():

    return render_template('results_panel.html')