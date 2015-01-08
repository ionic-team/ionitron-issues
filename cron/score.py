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


class Issue():
    """
    An abstraction over a github issue object used to calculate a score.
    """

    def __init__(self, **kwargs):
        """
        Initializes the object. If data hasn't been passed in, uses the issue
        id passed in to fetch the data required to initialize.
        @kwarg data: a dictionary containing issue data - see fetch_issue_data
        @kwarg iid: the issue id or number to be used to fetch data
        """
        redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
        self.db = redis.from_url(redis_url)

        if 'data' in kwargs:
            self.data = kwargs['data']

        elif 'iid' in kwargs:
            self.data = fetch_issue_data(kwargs['iid'])

        else:
            raise ValueError('Keyword argument not found. __init__ must\
                             receive one of the following keyword arguments:\
                             iid, data')
        self.score = 50
        self.login = self.data['user']['login']

    def get_score(self):
        """
        Calculates an opinionated score for an issue's priority.
        Priority score will start at 50, and can go up or down.
        Each function may or may not update the score based on it's result.
        The algorithm can be tweaked by changing values passed to each method.

        Not the most DRY, but it's explicit and obvious, and beats using a
        messy hack to call/chain all methods of the instance.
        @return: the issue's priority score, higher is better
        """
        self.core_team_member()
        self.each_contribution()
        self.account_is_new()
        self.each_year_since_account_created()
        self.every_x_followers()
        self.each_public_repo()
        self.each_issue_submitted_closed_by_bot()
        self.has_blog()
        self.image_provided()
        self.every_x_characters_in_body()
        self.demo_provided()
        self.daily_decay_since_creation()
        self.daily_decay_since_last_update()
        self.awaiting_reply()
        self.each_comment()
        return self.score

    ### Repo / Organization

    def core_team_member(self, add=80):
        if any([cvar['REPO_USERNAME'] in o['login'] for o in self.data['user_orgs']]):
            self.score += add

    def each_contribution(self, add=20):
        contrib = [c for c in self.data['contributors'] if self.login in self.data['contributors']]
        if contrib:
            self.score += min(100, (int(contrib[0]['contributions'])*add))

    ### User

    def account_is_new(self, subtract=10):
        created_at = datetime.datetime.strptime(self.data['user']['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        days_since = (datetime.datetime.now() - created_at).days
        if days_since < 180:
            self.score -= subtract

    def each_year_since_account_created(self, add=6):
        created_at = datetime.datetime.strptime(self.data['user']['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        days_since = (datetime.datetime.now() - created_at).days
        self.score += add * (days_since / 365)

    def every_x_followers(self, add=3, x=5):
        self.score += (add * (len(self.data['followers']) / x))

    def each_public_repo(self, add=2):
        self.score += (add * int(self.data['user']['public_repos']))

    def each_issue_submitted_closed_by_bot(self, subtract=20):
        bad_issues = [i for i in self.data['issues_closed_by_bot'] if i['user']['login'] is self.login]
        self.score -= min(100, (subtract * (len(bad_issues))))

    def has_blog(self, add=7):
        if self.data['user']['blog']:
            self.score += add

    ### Issue

    def image_provided(self, add=15):
        if re.search('<img.*</img>', self.data['issue']['body']):
            self.score += add

    def every_x_characters_in_body(self, add=1, x=200):
        self.score += (len(self.data['issue']['body']) / 200)

    def demo_provided(self, add=20):
        if re.search('(plnkr.co|codepen.io)', self.data['issue']['body']):
            self.score += add

    def daily_decay_since_creation(self, exp=1.05, start=50):
        created_at = datetime.datetime.strptime(self.data['issue']['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        days_since_creation = (datetime.datetime.now() - created_at).days
        self.score += float(start) - min((float(days_since_creation)**exp), start)

    def daily_decay_since_last_update(self, exp=1.20, start=15):
        updated_at = datetime.datetime.strptime(self.data['issue']['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        days_since_update = (datetime.datetime.now() - updated_at).days
        self.score += float(start) - min((float(days_since_update)**exp), start)

    def awaiting_reply(self, subtract=100):
        if set(cvar['NEEDS_REPLY_LABELS']).intersection(set(self.data['issue_labels'])):
            self.score -= subtract

    def each_comment(self, add=4):
        self.score += (len(self.data['issue_comments']) * add)
