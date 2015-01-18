import os
import json
import redis
import requests
from config.config import CONFIG_VARS as cvar


def fetch(key, path, data_expire=900):
    """
    Shortcut to call github's api.
    @param path: path/to/github/resource (string)
    @return a dictionary containing key:fetched data
    """

    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    db = redis.from_url(redis_url)

    auth = (cvar['GITHUB_ACCESS_TOKEN'], '')
    url = 'https://api.github.com%s' % path

    db_key = '%s:%s:fetch:%s' % (cvar['REPO_USERNAME'], cvar['REPO_ID'], url)
    cached_data = db.get(db_key)
    if cached_data:
        print 'fetched from db: %s' % path
        return json.loads(cached_data)

    print 'fetch: %s' % path

    data = {}
    try:
        r = requests.get(url, auth=auth)
        if r.status_code < 204:
            data[key] = r.json()
        else:
            data['error'] = r.text
            return data

    except Exception as ex:
        print 'fetch error, %s:, %s' % (path, ex)
        return { 'error': '%s' % ex, 'fetch': url }

    # Iterate through additional pages of data if available
    has_next = True if 'next' in r.links else False
    while has_next:
        try:
            url = r.links['next']['url']
            r = requests.get(url, auth=auth)
            if r.status_code < 204:
                data[key] += r.json()
                has_next = True if 'next' in r.links else False
            else:
                has_next = False
                data['error'] = r.text
                return data

        except Exception as ex:
            print 'fetch error, %s:, %s' % (path, ex)
            return { 'error': '%s' % ex, 'fetch': url }

    db.setex(db_key, json.dumps(data), data_expire)

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
    data = {}

    try:
        ### Data specific to this particular issue
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
            'user_orgs': '/users/%s/orgs' % data['issue']['user']['login']
        }
        for key, value in user_resources.iteritems():
            data.update(fetch(key, value, 60*60*24*7))

        repo_resources = {
            'contributors': '/repos/%s/%s/contributors' % (rname, rid),
            'team_members': '/orgs/%s/members' % rname
        }
        for key, value in repo_resources.iteritems():
            data.update(fetch(key, value, 60*60*24))

    except Exception as ex:
        print 'fetch_issue_data %s: %s' % (iid, ex)
        data['error'] = '%s: %s' % (iid, ex)

    return data
