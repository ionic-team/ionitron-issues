import requests
import threading
import os
import redis
import datetime
from worker import q
from cron.network import fetch
from cron.handlers import update_issue_score
from config.config import CONFIG_VARS as cvar


def queue_daily_tasks():
    print 'Queueing daily tasks...'

    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    db = redis.from_url(redis_url)

    # Do not update if scores have been updated within past 24 hours
    last_update = db.get('last_update')
    if last_update:
        then = datetime.datetime.fromordinal(last_update)
        now = datetime.datetime.now()
        if (now - then).days >= 1:
            q.enqueue(update_issue_scores)
            q.enqueue(issue_maintainence_tasks)
            db.set('last_update', now.toordinal())
    # Rerun daily tasks in 24 hours
    threading.Timer(60*60*24, queue_daily_tasks).start()


def issue_maintainence_tasks():
    print "Running daily tasks..."
    print map(lambda x: requests.get('http://ionitron-issues.herokuapp.com' + x), [
        '/api/close-old-issues',
        '/api/close-noreply-issues',
        '/api/warn-old-issues',
    ])


def update_issue_scores():
    """
    Recalculates the scores of all issues. Meant to run as a cron task.
    @kwarg iid: the id of a single issue to update (optional)
    """

    rname = cvar['REPO_USERNAME']
    rid = cvar['REPO_ID']
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    db = redis.from_url(redis_url)
    open_issues = fetch('issues', '/repos/%s/%s/issues?' % (rname, rid))['issues']

    # since we are recalculating all scores, remove data so that closed
    # issues aren't stored in the cache
    db.delete('issues')

    for i in open_issues:
        update_issue_score(int(i['number']))
