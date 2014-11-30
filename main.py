import json
import os
import requests
import datetime
import github3
from flask import Response, request, Flask, render_template
from config import CONFIG_VARS as cvar
from cron.issue import Issue

app = Flask(__name__)


@app.route("/")
def index():
    """
    @return: template containing docs and bot info
    """
    return render_template('index.html')


@app.route("/api/data")
def data():
    """
    @return: in the future, will return a static landing page
    """
    data = open('data.json').read()
    return Response(data, mimetype='application/json')


@app.route("/api/close-old-issues")
def cron_close_old_issues():
    """
    An endpoint for a cronjob to call.
    Closes issues older than REMOVAL_DAYS.
    @return: a JSON array containing the ids of closed issues
    """

    gh = github3.login(cvar['GITHUB_USERNAME'], cvar['GITHUB_PASSWORD'])
    repo = gh.repository(cvar['REPO_USERNAME'], cvar['REPO_ID'])
    issues = repo.iter_issues()

    try:  # Read message template from remote URL
        closing_msg = requests.get(cvar['CLOSING_TEMPLATE']).text
    except:  # Read from local file
        closing_msg = open(cvar['CLOSING_TEMPLATE']).read()

    closed = [Issue(i).close(msg=closing_msg) for i in issues]
    closed = filter(lambda x: x is not None, closed)

    return Response(json.dumps({'closed': closed}), mimetype='application/json')


@app.route("/api/warn-old-issues")
def cron_warn_old_issues():
    """
    An endpoint for a cronjob to call.
    Adds a warning message to issues older than REMOVAL_WARNING_DAYS..
    @return: a JSON array containing the ids of warned issues
    """
    gh = github3.login(cvar['GITHUB_USERNAME'], cvar['GITHUB_PASSWORD'])
    repo = gh.repository(cvar['REPO_USERNAME'], cvar['REPO_ID'])
    issues = repo.iter_issues()

    try:  # Read from remote URL
        warning_msg = requests.get(cvar['WARNING_TEMPLATE']).text
    except:  # Read from local file
        warning_msg = open(cvar['WARNING_TEMPLATE']).read()

    warned = [Issue(i).warn(msg=warning_msg) for i in issues]
    warned = filter(lambda x: x is not None, warned)

    return Response(json.dumps({'warned': warned}), mimetype='application/json')


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
