import json
import os
from flask import jsonify, request, Flask
import core.views

app = Flask(__name__)


@app.route("/")
def index():
    """
    @route('/')
    @return: in the future, will return a static landing page
    """
    return "Index"


@app.route("/(?P<user_id>\w+)/(?P<repo_id>\w+)")
def repo():
    """
    @route('/(?P<user_id>\w+)/(?P<repo_id>\w+)')
    @param(user_id): github user or organization id
    @param(repo_id): id/name of the repo on github
    @return: in the future, will return a template which contains an Angular app
    """
    return "Repo"


@app.route("/api/close-old-issues")
def cron_close_old_issues():
    """
    An endpoint for a cronjob to call.
    Closes issues older than REMOVAL_DAYS.
    @route('/api/close-old-issues')
    @return: a JSON array containing the ids of removed issues
    """
    data = core.views.close_old_issues()
    return jsonify(data)


@app.route("/api/warn-old-issues")
def cron_warn_old_issues():
    """
    An endpoint for a cronjob to call.
    Adds a warning message to issues older than REMOVAL_WARNING_DAYS..
    @route('/api/warn-old-issues')
    @return: a JSON array containing the ids of warned issues
    """
    data = core.views.warn_old_issues()
    return jsonify(data)


@app.route("/api/webook")
def webhook_router():
    body = json.loads(request.body)
    event_type = body['hook']['events']


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
