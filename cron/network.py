import datetime
import re
import os
import json
import redis
import requests
from config import CONFIG_VARS as cvar


def fetch(key, path):

    """
    Shortcut to call github's api.
    @param path: path/to/github/resource (string)
    @return a dictionary containing key:fetched data
    """
    auth = (cvar['GITHUB_USERNAME'], cvar['GITHUB_PASSWORD'])
    url = 'https://api.github.com' + path

    r = requests.get(url, auth=auth)
    data = {key: r.json()}

    # Iterate through additional pages of data if available
    has_next = True if 'next' in r.links else False
    while has_next:
        r = requests.get(r.links['next']['url'], auth=auth)
        data[key] += r.json()
        has_next = True if 'next' in r.links else False

    return data


def fetch_issue_data(iid):
    """
    Fetches all of the data required to calculate a score
    for an issue.
    @param iid: the id of the issue
    @return: a dictionary containing parsed JSON blobs
    """

    rname = cvar['REPO_USERNAME']
    rid = cvar['REPO_ID']
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    db = redis.from_url(redis_url)
    data = {}

    ### Data specific to this particular issue (do not cache)
    issue_resources = {
        'issue': '/repos/%s/%s/issues/%s' % (rname, rid, iid),
        'issue_comments': '/repos/%s/%s/issues/%s/comments' % (rname, rid, iid),
        'issue_labels': '/repos/%s/%s/issues/%s/labels' % (rname, rid, iid),
        'issue_events': '/repos/%s/%s/issues/%s/events' % (rname, rid, iid)
    }
    for key, value in issue_resources.iteritems():
        data.update(fetch(key, value))
    user_resources = {
        'user': '/users/%s' % data['issue']['user']['login'],
        'user_orgs': '/users/%s/orgs' % data['issue']['user']['login'],
        'followers': '/users/%s/followers' % data['issue']['user']['login']
    }
    for key, value in user_resources.iteritems():
        data.update(fetch(key, value))

    ### Slow-changing data applying to all issues (cache 24 hours)
    repo_data = db.get('repo_data') or {}
    if repo_data:
        repo_data = json.loads(repo_data)
        data.update(repo_data)
        return data
    repo_resources = {
        'collaborators': '/repos/%s/%s/collaborators' % (rname, rid),
        'contributors': '/repos/%s/%s/contributors' % (rname, rid),
        'team_members': '/orgs/%s/members' % rname,
        'issues_closed_by_bot': '/repos/%s/%s/issues?labels=%s' % (rname, rid, cvar['ON_CLOSE_LABEL'])
    }
    for key, value in repo_resources.iteritems():
        repo_data.update(fetch(key, value))
    db.setex('repo_data', json.dumps(repo_data), 60*60*24)
    data.update(repo_data)

    return data
