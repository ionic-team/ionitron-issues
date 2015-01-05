import json
import os
import threading
from flask import Response, request, Flask, render_template
from decorators import crossdomain
from cron.issue import close_old_issues, warn_old_issues
from cron.issue import close_noreply_issues
from webhooks.tasks import queue_daily_tasks
from webhooks.pull_request import validate_commit_messages
from webhooks.issue import flag_if_submitted_through_github, remove_needs_reply
from webhooks.issue_updated import remove_notice_if_valid


# Initialize daily tasks queue loop
threading.Thread(target=queue_daily_tasks).start()
app = Flask(__name__)


@app.route("/")
def index():
    """
    @return: template containing docs and bot info
    """
    return render_template('index.html')


@app.route("/api/close-old-issues", methods=['GET', 'POST'])
def cron_close_old_issues():
    """
    An endpoint for a cronjob to call.
    Closes issues older than REMOVAL_DAYS.
    """

    t = threading.Thread(target=close_old_issues)
    t.start()
    msg = 'close_old_issues task forked to background'

    return Response(json.dumps({'message': msg}), mimetype='application/json')


@app.route("/api/close-noreply-issues", methods=['GET', 'POST'])
def cron_close_noreply_issues():
    """
    An endpoint for a cronjob to call.
    Closes issues that never received a requested reply.
    """

    t = threading.Thread(target=close_noreply_issues)
    t.start()
    msg = 'close_noreply_issues task forked to background'

    return Response(json.dumps({'message': msg}), mimetype='application/json')


@app.route("/api/warn-old-issues", methods=['GET', 'POST'])
def cron_warn_old_issues():
    """
    An endpoint for a cronjob to call.
    Adds a warning message to issues older than REMOVAL_WARNING_DAYS.
    """

    t = threading.Thread(target=warn_old_issues)
    t.start()
    msg = 'warn_old_issues task forked to background'

    return Response(json.dumps({'message': msg}), mimetype='application/json')


@app.route("/api/webhook", methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type', 'X-Github-Event'])
def webhook_router():

    response = []
    event_type = request.headers['X-Github-Event']
    if request.data:
        payload = json.loads(request.data)

    if event_type == 'pull_request':
        response.append(validate_commit_messages(payload))

    if event_type == 'issues':
        response.append(flag_if_submitted_through_github(payload))

    if event_type == 'issue_updated':
        response.append(remove_notice_if_valid(request.args['issueNum']))

    if event_type == 'issue_comment':
        response.append(remove_needs_reply(payload))


    return Response(json.dumps(response), mimetype='application/json')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
