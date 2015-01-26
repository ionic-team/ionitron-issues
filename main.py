import os
import json
import threading
from flask import Response, request, Flask, render_template, send_from_directory, redirect
import wsgioauth2
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

if not cvar['DEBUG']:
    service = wsgioauth2.GitHubService(allowed_orgs=['driftyco'])
    client = service.make_client(client_id=os.environ['IONITRON_ISSUES_CLIENT_ID'],
                                 client_secret=os.environ['IONITRON_ISSUES_CLIENT_SECRET'],)
    app.wsgi_app = client.wsgi_middleware(app.wsgi_app,
                                          secret=os.environ['IONITRON_ISSUES_SECRET_KEY'],
                                          login_path='/app')


@app.route("/")
def login():
    try:
        if not cvar['DEBUG']:
            return redirect(client.make_authorize_url('http://ionitron-issues.herokuapp.com/app/'))
        else:
            return redirect('/app/')
    except Exception as ex:
        print 'login %s' % ex


@app.route("/app/")
def app_index():
    try:
        return render_template('index.html')
    except Exception as ex:
        print 'index %s' % ex


@app.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(app.static_folder, filename)


@app.route("/app/maintainence/<path:number>", methods=['GET', 'POST'])
def issue_maintainence(number):
    data = {}
    try:
        from tasks.maintainence import issue_maintainence_number
        data = issue_maintainence_number(number)
    except Exception as ex:
        print 'issue_maintainence error: %s' % ex
        data['error'] = '%s' % ex
    return Response(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')


@app.route("/app/maintainence", methods=['GET', 'POST'])
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


@app.route("/app/issue-scores", methods=['GET', 'POST'])
def get_issue_scores():
    """
    Gets the scores calculated for all open issues.
    """
    data = {}
    try:
        from tasks.issue_scores import get_issue_scores
        data = get_issue_scores()
    except Exception as ex:
        print 'get_issue_scores error: %s' % ex
        data = { 'error' : '%s' % ex }
    return Response(json.dumps(data), mimetype='application/json')


@app.route("/app/issue-response", methods=['POST'])
def issue_response():
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
