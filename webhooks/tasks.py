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
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    db = redis.from_url(redis_url)

    # Do not update if scores have been updated within past 24 hours
    last_update = db.get('last_update')
    print 'Queueing daily tasks, last update: %s' % last_update

    if last_update:
        then = datetime.datetime.fromordinal(int(last_update))
        now = datetime.datetime.now()
        if (now - then).days >= 1:
            q.enqueue(update_issue_scores)
            q.enqueue(issue_maintainence_tasks)
            db.set('last_update', now.toordinal())
    else:  # last update time hasn't been set. Set it so it runs in 24 hours
        db.set('last_update', datetime.datetime.now().toordinal())

    # Rerun daily tasks in 24 hours
    threading.Timer(60*60*24, queue_daily_tasks).start()


def issue_maintainence_tasks():
    """
    Maintainence tasks to run on older issues.
    """
    print "Running daily tasks..."
    print map(lambda x: requests.get('http://ionitron-issues.herokuapp.com' + x), [
        '/api/close-old-issues',
        '/api/manage-needs-reply-issues',
        '/api/warn-old-issues',
    ])


def update_issue_scores():
    """
    Recalculates the scores of all issues. Meant to be run as a cron task.
    """
    print 'update_issue_scores'

    rname = cvar['REPO_USERNAME']
    rid = cvar['REPO_ID']
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    db = redis.from_url(redis_url)
    data = fetch('issues', '/repos/%s/%s/issues?' % (rname, rid))

    open_issues = data.get('issues')
    if data.get('error') or not open_issues:
        return data

    print 'open issues: %s' % len(open_issues)

    for i in open_issues:
        try:
            issue_number = int(i.get('number', 0))
            if issue_number > 0:
                update_issue_score(issue_number, throttle_recalculation=True)

        except Exception as ex:
            print ex

    return {
        'org': rname,
        'repo': rid,
        'open_issues': len(open_issues)
    }
