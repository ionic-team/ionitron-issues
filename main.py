import os
import json
import threading
from flask import Response, request, Flask, render_template, send_from_directory, redirect
from decorators import crossdomain
from config.config import CONFIG_VARS as cvar
from flask.ext.sqlalchemy import SQLAlchemy
import urlparse
import requests
import github_api


# Initialize daily/hourly tasks queue loop
if not cvar['DEBUG']:
    from tasks.maintainence import queue_daily_tasks
    threading.Thread(target=queue_daily_tasks).start()
    threading.Timer(60*60*24, queue_daily_tasks).start()

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['HEROKU_POSTGRESQL_ONYX_URL']
db = SQLAlchemy(app)


@app.route("/", methods=['GET', 'POST'])
def apps_index():
    try:
        client_id = os.environ['IONITRON_ISSUES_CLIENT_ID']
        client_secret = os.environ['IONITRON_ISSUES_CLIENT_SECRET']
        code = request.args.get('code')
        if not code:
            # not signed in
            return redirect('https://github.com/login/oauth/authorize?client_id=%s' % (client_id))

        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code
        }
        url = 'https://github.com/login/oauth/access_token'
        rsp = requests.get(url, params=params)
        rsp_dict = urlparse.parse_qs(rsp.text)
        access_token = rsp_dict["access_token"]
        
        if not access_token or len(access_token) < 1:
            return redirect('https://github.com/login/oauth/authorize?client_id=%s' % (client_id))

        user_req = requests.get('https://api.github.com/user', auth=(access_token[0], ''))
        print user_req.json()

        # jimthedev
        logins = github_api.is_org_admin_membership('driftyco', 'adamdbradley')
        print logins
        print logins

        return render_template('index.html')
    except Exception as ex:
        print 'index %s' % ex


@app.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(app.static_folder, filename)


@app.route("/api/<path:repo_username>/<path:repo_id>/<path:number>/maintainence", methods=['GET', 'POST'])
def issue_maintainence(repo_username, repo_id, number):
    data = {}
    try:
        from tasks.maintainence import issue_maintainence_number
        data = issue_maintainence_number(repo_username, repo_id, number)
    except Exception as ex:
        print 'issue_maintainence error: %s' % ex
        data['error'] = '%s' % ex
    return Response(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')


@app.route("/api/maintainence", methods=['GET', 'POST'])
def all_issues_maintainence():
    data = {}
    try:
        from tasks.maintainence import run_maintainence_tasks
        t = threading.Thread(target=run_maintainence_tasks)
        t.start()
        data['message'] = 'all_issues_maintainence task forked to background'
    except Exception as ex:
        print 'all_issues_maintainence error: %s' % ex
        data['error'] = '%s' % ex
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/api/<path:repo_username>/<path:repo_id>/issue-scores", methods=['GET', 'POST'])
def get_issue_scores(repo_username, repo_id):
    """
    Gets the scores calculated for all open issues.
    """
    data = {}
    try:
        from tasks.issue_scores import get_issue_scores
        data = get_issue_scores(repo_username, repo_id)
    except Exception as ex:
        print 'get_issue_scores error: %s' % ex
        data = { 'error' : '%s' % ex }
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/api/<path:repo_username>/<path:repo_id>/issue-response", methods=['POST'])
def issue_response(repo_username, repo_id):
    data = {}
    try:
        from tasks.send_response import submit_issue_response
        payload = json.loads(request.data)
        data = submit_issue_response(repo_username,
                                     repo_id,
                                     payload.get('number'),
                                     payload.get('action_type'),
                                     payload.get('message_type'),
                                     payload.get('custom_message'))
    except Exception as ex:
        print 'issue_response error: %s' % ex
        data = { 'error' : '%s' % ex }
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/webhook", methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type', 'X-Github-Event'])
def github_webhook():
    data = {}
    try:
        event_type = request.headers.get('X-Github-Event')
        if event_type and request.data:
            from tasks.webhooks import receive_webhook
            data = receive_webhook(event_type, json.loads(request.data))
        else:
            data['error'] = 'missing event_type or request.data'

    except Exception as ex:
        print 'github_webhook error: %s' % ex
        data['error'] = '%s' % ex

    return Response(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print 'Server started, port %s' % port
    app.run(host='0.0.0.0', port=port)
