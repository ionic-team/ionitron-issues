import datetime
import re
from config.config import CONFIG_VARS as cvar
from cron.network import fetch_issue_data


class Scorer():
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
        self.number_of_comments = 0
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
        self.has_code_snippet()
        self.has_forum_link()
        return int(self.score)

    ### Repo / Organization

    def core_team_member(self, add=cvar['CORE_TEAM']):
        if any([cvar['REPO_USERNAME'] in o['login'] for o in self.data['user_orgs']]):
            self.score += add

    def each_contribution(self, add=cvar['CONTRIBUTION']):
        contrib = [c for c in self.data['contributors'] if self.login in self.data['contributors']]
        if contrib:
            self.score += min(100, (int(contrib[0]['contributions'])*add))

    ### User

    def account_is_new(self, subtract=cvar['NEW_ACCOUNT']):
        created_at = datetime.datetime.strptime(self.data['user']['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        days_since = (datetime.datetime.now() - created_at).days
        if days_since < 180:
            self.score -= subtract

    def each_year_since_account_created(self, add=cvar['GITHUB_YEARS']):
        created_at = datetime.datetime.strptime(self.data['user']['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        days_since = (datetime.datetime.now() - created_at).days
        self.score += add * (days_since / 365)

    def every_x_followers(self, add=cvar['FOLLOWERS_ADD'], x=cvar['FOLLOWERS_X']):
        self.score += (add * (len(self.data['followers']) / x))

    def each_public_repo(self, add=cvar['PUBLIC_REPOS']):
        self.score += min((add * int(self.data['user']['public_repos'])), 30)

    def each_issue_submitted_closed_by_bot(self, subtract=cvar['BOT_CLOSED']):
        bad_issues = [i for i in self.data['issues_closed_by_bot'] if i['user']['login'] is self.login]
        self.score -= min(100, (subtract * (len(bad_issues))))

    def has_blog(self, add=cvar['BLOG']):
        if 'blog' in self.data['user']:
            if self.data['user']['blog']:
                self.score += add

    ### Issue

    def image_provided(self, add=cvar['IMAGE']):
        if re.search('<img.*</img>', (self.data['issue']['body'] or '')):
            self.score += add

    def every_x_characters_in_body(self, add=cvar['CHAR_ADD'], x=cvar['CHAR_X']):
        if self.data['issue']['body']:
            self.score += (len(self.data['issue']['body']) / 200)

    def demo_provided(self, add=cvar['DEMO']):
        if re.search('(plnkr.co|codepen.io)', (self.data['issue']['body'] or '')):
            self.score += add

    def daily_decay_since_creation(self, exp=1.05, start=cvar['CREATED_START']):
        created_at = datetime.datetime.strptime(self.data['issue']['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        self.created_at_str = created_at.isoformat()
        days_since_creation = abs((datetime.datetime.now() - created_at).days)
        self.score += (float(start) - min((float(days_since_creation)**exp), start))

    def daily_decay_since_last_update(self, exp=1.20, start=cvar['UPDATE_START']):
        updated_at = datetime.datetime.strptime(self.data['issue']['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        self.updated_at_str = updated_at.isoformat()
        days_since_update = abs((datetime.datetime.now() - updated_at).days)
        self.score += (float(start) - min((float(days_since_update)**exp), start))

    def awaiting_reply(self, subtract=cvar['AWAITING_REPLY']):
        if self.data['issue_labels']:
            label_set = set([l['name'] for l in self.data['issue_labels']])
            if set(cvar['NEEDS_REPLY_LABELS']).intersection(label_set):
                self.score -= subtract

    def each_comment(self, add=cvar['COMMENT']):
        if self.data['issue_comments']:
            self.number_of_comments = len(self.data['issue_comments'])
            self.score += (self.number_of_comments * add)

    def has_code_snippet(self, add=cvar['SNIPPET']):
        if re.search('```', (self.data['issue']['body'] or '')):
            self.score += add

    def has_forum_link(self, add=cvar['FORUM_ADD'], forum_url=cvar['FORUM_URL']):
        if re.search(forum_url, (self.data['issue']['body'] or '')):
            self.score += add
