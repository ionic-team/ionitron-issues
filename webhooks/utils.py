import requests


def daily_tasks():

    # Runs the following cron jobs and writes results to log
    print map(lambda x: requests.get('http://ionitron-issues.herokuapp.com' + x), [
        '/api/close-old-issues',
        '/api/close-noreply-issues',
        '/api/warn-old-issues',
    ])
