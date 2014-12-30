import json
import os
import requests
import github3
from flask import Response, request, Flask, render_template
from config import CONFIG_VARS as cvar
from cron.issue import Issue
from webhooks.pull_request import validate_commit_messages
from webhooks.issue import flag_if_submitted_through_github, \
    remove_flag_if_valid

app = Flask(__name__)


@app.route("/")
def index():
    """
    @return: template containing docs and bot info
    """
    return render_template('index.html')


@app.route("/api/close-old-issues", methods=['POST'])
def cron_close_old_issues():
    """
    An endpoint for a cronjob to call.
    Closes issues older than REMOVAL_DAYS.
    @return: a JSON array containing the ids of closed issues
    """

    gh = github3.login(cvar['GITHUB_USERNAME'], cvar['GITHUB_PASSWORD'])
    repo = gh.repository(cvar['REPO_USERNAME'], cvar['REPO_ID'])
    issues = repo.iter_issues()

    try:  # Read message templates from remote URL
        msg = requests.get(cvar['CLOSING_TEMPLATE']).text
    except:  # Read from local file
        msg = open(cvar['CLOSING_TEMPLATE']).read()

    closed = [Issue(i).close(msg=msg, reason='old') for i in issues]
    closed = filter(lambda x: x is not None, closed)

    return Response(json.dumps({'closed': closed}), mimetype='application/json')


@app.route("/api/close-noreply-issues", methods=['POST'])
def cron_noreply_issues():
    """
    An endpoint for a cronjob to call.
    Closes issues that never received a requested reply.
    @return: a JSON array containing the ids of closed issues
    """

    gh = github3.login(cvar['GITHUB_USERNAME'], cvar['GITHUB_PASSWORD'])
    repo = gh.repository(cvar['REPO_USERNAME'], cvar['REPO_ID'])
    issues = repo.iter_issues()

    try:  # Read message templates from remote URL
        msg = requests.get(cvar['CLOSING_NOREPLY_TEMPLATE']).text
    except:  # Read from local file
        msg = open(cvar['CLOSING_NOREPLY_TEMPLATE']).read()

    closed = [Issue(i).close(msg=msg, reason='noreply') for i in issues]
    closed = filter(lambda x: x is not None, closed)

    return Response(json.dumps({'closed': closed}), mimetype='application/json')


@app.route("/api/warn-old-issues", methods=['POST'])
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


@app.route("/api/webhook", methods=['GET', 'POST'])
def webhook_router():

    event_type = request.headers['X-Github-Event']
    payload = json.loads(request.data)
    response = []

    if event_type == 'pull_request':
        response.append(validate_commit_messages(payload))

    if event_type == 'issues':
        response.append(flag_if_submitted_through_github(payload))
        response.append(remove_flag_if_valid(payload))

    return Response(json.dumps(response), mimetype='application/json')


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
