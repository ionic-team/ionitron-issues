import json
import os
import requests
import datetime
import github3
from flask import Response, request, Flask, render_template
from config import CONFIG_VARS as cvar
from cron.issue import Issue
from webhooks.pull_request import validate_commit_messages

app = Flask(__name__)


def github_event(argument):

    def decorator(func):

        def wrapper(*args, **kwargs):
            try:
                event_type = request.headers['X-Github-Event']
            except:
                event_type = ''
            if argument == event_type:
                return func(*args, **kwargs)
            else:
                return Response('Could not find handler for that event.\n', 404)
        return wrapper
    return decorator


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


@github_event('pull_request')
@app.route("/api/webhook", methods=['GET', 'POST'])
def webhook_pull_request():
    """
    Responds to a pull_request event by validating the format of it's commit messages.
    Based off of https://github.com/btford/poppins-check-commit
    @return: JSON response containing dictionary object:
        'pr_title': whether or not pull message is valid (bool),
        'commits': {
                commit_sha: whether or not commit message is valid (bool)
        }

    """
    data = json.loads(request.data)
    result = validate_commit_messages(data)
    return Response(json.dumps(result), mimetype='application/json')


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
