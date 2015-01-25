import os
import json
import threading
from flask import Response, request, Flask, render_template, send_from_directory
import heroku_bouncer
from decorators import crossdomain
from config.config import CONFIG_VARS as cvar
from flask.ext.sqlalchemy import SQLAlchemy


# Initialize daily/hourly tasks queue loop
if not cvar['DEBUG']:
    from tasks.maintainence import queue_daily_tasks
    threading.Thread(target=queue_daily_tasks).start()

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['HEROKU_POSTGRESQL_ONYX_URL']
db = SQLAlchemy(app)
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


@app.route("/api/maintainence/<path:number>", methods=['GET', 'POST'])
def issue_maintainence(number):
    if not has_access():
        return forbidden_access()

    data = {}
    try:
        from tasks.maintainence import issue_maintainence_number
        data = issue_maintainence_number(number)
    except Exception as ex:
        print 'issue_maintainence error: %s' % ex
        data['error'] = '%s' % ex
    return Response(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')


@app.route("/api/maintainence", methods=['GET', 'POST'])
def all_issues_maintainence():
    if not has_access():
        return forbidden_access()

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


@app.route("/api/issue-scores", methods=['GET', 'POST'])
def get_issue_scores():
    """
    Gets the scores calculated for all open issues.
    """
    if not has_access():
        return forbidden_access()

    data = {}
    try:
        from tasks.issue_scores import get_issue_scores
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
        from tasks.send_response import submit_issue_response
        payload = json.loads(request.data)
        data = submit_issue_response(payload.get('number'),
                                     payload.get('action_type'),
                                     payload.get('message_type'),
                                     payload.get('custom_message'))
    except Exception as ex:
        print 'issue_response error: %s' % ex
        data = { 'error' : '%s' % ex }
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/api/webhook", methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['Content-Type', 'X-Github-Event'])
def github_webhook():
    try:
        event_type = request.headers.get('X-Github-Event')
        if event_type and request.data:
            from tasks.webhooks import receive_webhook
            receive_webhook(event_type, json.loads(request.data))

        return Response('got it ;)')

    except Exception as ex:
        print 'github_webhook error: %s' % ex
        return Response('sadpanda')



def has_access():
    user = request.environ.get('REMOTE_USER')
    if user is not None:
        return user.lower().endswith('@drifty.com')
    return False


def forbidden_access():
    return Response(json.dumps({
        'error': 'Forbidden Access'
    }), mimetype='application/json', status_code=403)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print 'Server started, port %s' % port
    app.run(host='0.0.0.0', port=port)
