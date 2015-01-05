import requests
import threading
from worker import q


def queue_daily_tasks():
    print 'Queueing daily tasks...'
    q.enqueue(daily_tasks)
    threading.Timer(5, queue_daily_tasks).start()


def daily_tasks():
    print "Running daily tasks..."
    print map(lambda x: requests.get('http://ionitron-issues.herokuapp.com' + x), [
        '/api/close-old-issues',
        '/api/close-noreply-issues',
        '/api/warn-old-issues',
    ])
