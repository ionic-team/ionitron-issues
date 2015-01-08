import datetime
import re
from config import CONFIG_VARS as cvar
from cron.network import fetch_issue_data


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
        if 'blog' in self.data['user']:
            if self.data['user']['blog']:
                self.score += add

    ### Issue

    def image_provided(self, add=15):
        if re.search('<img.*</img>', (self.data['issue']['body'] or '')):
            self.score += add

    def every_x_characters_in_body(self, add=1, x=200):
        if self.data['issue']['body']:
            self.score += (len(self.data['issue']['body']) / 200)

    def demo_provided(self, add=20):
        if re.search('(plnkr.co|codepen.io)', (self.data['issue']['body'] or '')):
            self.score += add

    def daily_decay_since_creation(self, exp=1.05, start=50):
        created_at = datetime.datetime.strptime(self.data['issue']['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        days_since_creation = abs((datetime.datetime.now() - created_at).days)
        self.score += (float(start) - min((float(days_since_creation)**exp), start))

    def daily_decay_since_last_update(self, exp=1.20, start=15):
        updated_at = datetime.datetime.strptime(self.data['issue']['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        days_since_update = abs((datetime.datetime.now() - updated_at).days)
        self.score += (float(start) - min((float(days_since_update)**exp), start))

    def awaiting_reply(self, subtract=100):
        if self.data['issue_labels']:
            label_set = set([l['name'] for l in self.data['issue_labels']])
            if set(cvar['NEEDS_REPLY_LABELS']).intersection(label_set):
                self.score -= subtract

    def each_comment(self, add=4):
        if self.data['issue_comments']:
            self.score += (len(self.data['issue_comments']) * add)
