import json
import os
import threading
from flask import Response, request, Flask, render_template
from flask import send_from_directory
from decorators import crossdomain
from cron.issue import close_old_issues, warn_old_issues, test_api_access
from cron.issue import close_noreply_issues
from cron.handlers import get_issue_scores, update_issue_score
from webhooks.tasks import queue_daily_tasks, update_issue_scores
from webhooks.pull_request import validate_commit_messages
from webhooks.issue import flag_if_submitted_through_github, remove_needs_reply
from webhooks.issue_updated import remove_notice_if_valid


# Initialize daily/hourly tasks queue loop
threading.Thread(target=queue_daily_tasks).start()
app = Flask(__name__, static_folder='static')


@app.route("/")
def index():
    """
    @return: template containing docs and bot info
    """
    return render_template('index.html')


@app.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(app.static_folder, filename)


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


@app.route("/api/issue-scores", methods=['GET', 'POST'])
def issue_scores():
    """
    Gets the scores calculated for all open issues.
    @return: {iid: score}
    """
    try:
        data = get_issue_scores()
    except Exception as ex:
        print 'get_issue_scores error: %s' % ex
        data = { 'error' : '%s' % ex }

    return Response(json.dumps(data), mimetype='application/json')


@app.route("/api/calculate-issue-scores", methods=['GET', 'POST'])
def calculate_issue_scores():
    """
    Re-calculates the scores for all open issues.
    """
    try:
        data = update_issue_scores()
    except Exception as ex:
        print 'calculate_issue_scores error: %s' % ex
        data = { 'error' : '%s' % ex }
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/api/test", methods=['GET', 'POST'])
def api_test():
    try:
        data = test_api_access()
    except Exception as ex:
        print 'api_test error: %s' % ex
        data = { 'error' : '%s' % ex }
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/api/webhook", methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type', 'X-Github-Event'])
def webhook_router():

    response = []
    event_type = request.headers['X-Github-Event']
    if request.data:
        payload = json.loads(request.data)

    if event_type == 'pull_request':
        response.append(validate_commit_messages(payload))
        response.append(update_issue_score(payload['pull_request']['number']))

    if event_type == 'issues':
        response.append(flag_if_submitted_through_github(payload))

    if event_type == 'issue_updated':
        response.append(remove_notice_if_valid(request.args['issueNum']))
        response.append(update_issue_score(request.args['issueNum']))

    if event_type == 'issue_comment':
        response.append(remove_needs_reply(payload))
        response.append(update_issue_score(payload['issue']['number']))

    # add additional event handlers here
    # full list of event types: https://developer.github.com/webhooks/#events

    return Response(json.dumps(response), mimetype='application/json')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print 'Server started, port %s' % port
    app.run(host='0.0.0.0', port=port)
