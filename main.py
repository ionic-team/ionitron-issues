import json
import os
import threading
from flask import Response, request, Flask, render_template, session
from flask import send_from_directory
import heroku_bouncer
from decorators import crossdomain
from cron.issue import close_old_issues, warn_old_issues, test_api_access, submit_issue_response
from cron.issue import close_noreply_issues
from cron.handlers import get_issue_scores, update_issue_score
from webhooks.tasks import queue_daily_tasks, update_issue_scores
from webhooks.pull_request import validate_commit_messages
from webhooks.issue import flag_if_submitted_through_github, remove_needs_reply
from webhooks.issue_updated import remove_notice_if_valid
from config.config import CONFIG_VARS as cvar


# Initialize daily/hourly tasks queue loop
if not cvar['DEBUG']:
    threading.Thread(target=queue_daily_tasks).start()

app = Flask(__name__, static_folder='static')
app.wsgi_app = heroku_bouncer.bouncer(app.wsgi_app)


@app.route("/")
def index():
    """
    @return: template containing docs and bot info
    """
    if not has_access():
        return forbidden_access()

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
    if not has_access():
        return forbidden_access()

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
    if not has_access():
        return forbidden_access()

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
    if not has_access():
        return forbidden_access()

    t = threading.Thread(target=warn_old_issues)
    t.start()
    msg = 'warn_old_issues task forked to background'

    return Response(json.dumps({'message': msg}), mimetype='application/json')


@app.route("/api/calculate-issue-scores", methods=['GET', 'POST'])
def calculate_issue_scores():
    """
    Re-calculates the scores for all open issues.
    """
    if not has_access():
        return forbidden_access()

    data = {}
    try:
        t = threading.Thread(target=update_issue_scores)
        t.start()
        data['message'] = 'calculate_issue_scores task forked to background'
    except Exception as ex:
        print 'calculate_issue_scores error: %s' % ex
        data['error'] = '%s' % ex
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/api/issue-scores", methods=['GET', 'POST'])
def issue_scores():
    """
    Gets the scores calculated for all open issues.
    @return: {iid: score}
    """
    if not has_access():
        return forbidden_access()

    data = {}
    try:
        data = get_issue_scores()
    except Exception as ex:
        print 'get_issue_scores error: %s' % ex
        data = { 'error' : '%s' % ex }
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/api/issue-response", methods=['POST'])
def issue_response():
    if not has_access():
        return forbidden_access()

    data = {}
    try:
        payload = json.loads(request.data)
        data = submit_issue_response(payload.get('iid'), payload.get('action_type'), payload.get('message_type'), payload.get('custom_message'))
    except Exception as ex:
        print 'issue_response error: %s' % ex
        data = { 'error' : '%s' % ex }
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/api/test", methods=['GET', 'POST'])
def api_test():
    if not has_access():
        return forbidden_access()

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


def has_access():
    user = request.environ.get('REMOTE_USER')
    if user is not None:
        user_domain = user.lower().strip().split('@')
        if len(user_domain) == 2:
            return user_domain[1] == 'drifty.com'
    return False


def forbidden_access():
    return Response(json.dumps({
        'error': 'Forbidden Access'
    }), mimetype='application/json', status_code=403)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print 'Server started, port %s' % port
    app.run(host='0.0.0.0', port=port)
