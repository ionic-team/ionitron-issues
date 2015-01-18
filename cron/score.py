import datetime
import re
from config.config import CONFIG_VARS as cvar


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
            from cron.network import fetch_issue_data
            self.data = fetch_issue_data(kwargs['iid'])

        else:
            raise ValueError('Keyword argument not found. __init__ must\
                             receive one of the following keyword arguments:\
                             iid, data')
        self.score = 0
        self.number_of_comments = 0
        self.score_data = {}

        self.user = self.data.get('user', {})
        self.login = ''
        if self.user:
            self.login = self.user.get('login', '')

        self.issue = self.data.get('issue', {})
        self.body = ''
        if self.issue:
            self.body = self.issue.get('body', '')


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
        self.each_public_gist()
        self.has_blog()
        self.images_provided()
        self.every_x_characters_in_body()
        self.code_demos()
        self.daily_decay_since_creation()
        self.daily_decay_since_last_update()
        self.awaiting_reply()
        self.each_comment()
        self.code_snippets()
        self.has_forum_link()
        self.has_links()
        self.has_issue_reference()

        return int(self.score)


    ### Repo / Organization

    def core_team_member(self, add=cvar['CORE_TEAM']):
        user_orgs = self.data.get('user_orgs')
        if user_orgs:
            if any([cvar['REPO_USERNAME'] in o.get('login') for o in user_orgs]):
                self.score += add
                self.score_data['core_team_member'] = add


    def each_contribution(self, add=cvar['CONTRIBUTION']):
        contributors = self.data.get('contributors')
        if not contributors:
            return
        contrib = [c for c in contributors if self.login == c.get('login')]
        if contrib and len(contrib):
            contributions = contrib[0].get('contributions')
            if contributions:
                val = min(100, (int(contributions)*add))
                self.score += val
                if val > 0:
                    self.score_data['each_contribution'] = val


    ### User

    def account_is_new(self, subtract=cvar['NEW_ACCOUNT'], now=datetime.datetime.now()):
        created_at_data = self.user.get('created_at')
        if not created_at_data:
            return
        created_at = datetime.datetime.strptime(created_at_data, '%Y-%m-%dT%H:%M:%SZ')
        days_since = (now - created_at).days

        if days_since < 3:
            self.score -= subtract * 10
            self.score_data['account_is_new'] = subtract * -1

        elif days_since < 90:
            self.score -= subtract
            self.score_data['account_is_new'] = subtract * -1


    def each_year_since_account_created(self, add=cvar['GITHUB_YEARS'], now=datetime.datetime.now()):
        created_at_data = self.user.get('created_at')
        if not created_at_data:
            return
        created_at = datetime.datetime.strptime(created_at_data, '%Y-%m-%dT%H:%M:%SZ')
        days_since = (now - created_at).days
        val = add * (days_since / 365)
        self.score += val
        if val > 0:
            self.score_data['each_year_since_account_created'] = val


    def every_x_followers(self, add=cvar['FOLLOWERS_ADD'], x=cvar['FOLLOWERS_X']):
        followers = self.user.get('followers')
        if followers:
            val = (add * (int(followers) / x))
            self.score += val
            if val > 0:
                self.score_data['every_x_followers'] = val


    def each_public_repo(self, add=cvar['PUBLIC_REPOS']):
        public_repos = self.user.get('public_repos')
        if public_repos:
            val = min((add * int(public_repos)), 50)
            self.score += val
            if val > 0:
                self.score_data['each_public_repo'] = val


    def each_public_gist(self, add=cvar['PUBLIC_GISTS']):
        public_gists = self.user.get('public_gists')
        if public_gists:
            val = min((add * int(public_gists)), 30)
            self.score += val
            if val > 0:
                self.score_data['each_public_gist'] = val


    def has_blog(self, add=cvar['BLOG']):
        blog = self.user.get('blog')
        if blog:
            self.score += add
            self.score_data['has_blog'] = add



    ### Issue

    def images_provided(self, add=cvar['IMAGE']):
        val = self.total_images(self.body)

        comments = self.data.get('issue_comments')
        if comments:
            for c in comments:
                val += self.total_images(c.get('body', ''))

        self.score += val
        if val > 0:
            self.score_data['images_provided'] = val


    def total_images(self, text):
        return len(re.findall('<img ', text)) + len(re.findall('!\[', text))


    def every_x_characters_in_body(self, add=cvar['CHAR_ADD'], x=cvar['CHAR_X']):
        val = (len(self.body) / x)
        self.score += val
        if val > 0:
            self.score_data['every_x_characters_in_body'] = val


    def code_demos(self, add=cvar['DEMO'], demo_domains=cvar['DEMO_DOMAINS']):
        val = 0
        for demo_domain in demo_domains:
            val += len(re.findall(demo_domain, self.body))
        self.score += val
        if val > 0:
            self.score_data['code_demos'] = val


    def daily_decay_since_creation(self, exp=cvar['CREATION_DECAY_EXP'], start=cvar['CREATED_START'], now=datetime.datetime.now()):
        created_at_data = self.issue.get('created_at')
        if not created_at_data:
            return
        created_at = datetime.datetime.strptime(created_at_data, '%Y-%m-%dT%H:%M:%SZ')
        self.created_at_str = created_at.isoformat()
        days_since_creation = abs((now - created_at).days)
        val = (float(start) - min((float(days_since_creation)**exp), start))
        self.score += val
        if val > 0:
            self.score_data['daily_decay_since_creation'] = val
        return {
            'created_at_str': self.created_at_str,
            'days_since_creation': days_since_creation,
            'exp': exp,
            'start': start,
            'score': val
        }


    def daily_decay_since_last_update(self, exp=cvar['LAST_UPDATE_DECAY_EXP'], start=cvar['UPDATE_START'], now=datetime.datetime.now()):
        updated_at_data = self.issue.get('updated_at')
        if not updated_at_data:
            return
        updated_at = datetime.datetime.strptime(updated_at_data, '%Y-%m-%dT%H:%M:%SZ')
        self.updated_at_str = updated_at.isoformat()
        days_since_update = abs((now - updated_at).days)
        val = (float(start) - min((float(days_since_update)**exp), start))
        self.score += val
        if val > 0:
            self.score_data['daily_decay_since_last_update'] = val
        return {
            'updated_at_str': self.updated_at_str,
            'days_since_update': days_since_update,
            'exp': exp,
            'start': start,
            'score': val
        }


    def awaiting_reply(self, subtract=cvar['AWAITING_REPLY']):
        issue_labels = self.data.get('issue_labels')
        if issue_labels:
            label_set = set([l['name'] for l in issue_labels])
            if set(cvar['NEEDS_REPLY_LABELS']).intersection(label_set):
                self.score -= subtract
                self.score_data['awaiting_reply'] = subtract * -1


    def each_comment(self, add=cvar['COMMENT']):
        comments = self.data.get('issue_comments')
        if comments:
            self.number_of_comments = len(comments)
            val = (self.number_of_comments * add)
            self.score += val
            if val > 0:
                self.score_data['each_comment'] = val


    def code_snippets(self, add=cvar['SNIPPET'], per_line=cvar['SNIPPET_LINE'], line_max=cvar['SNIPPET_LINE_MAX']):
        total_code_lines = self.total_code_lines(self.body)

        comments = self.data.get('issue_comments')
        if comments:
            for c in comments:
                total_code_lines += self.total_code_lines(c.get('body', ''))

        if total_code_lines > 0:
            val = add
            total_code_lines = min(total_code_lines, line_max)
            val += total_code_lines * per_line

            self.score += val
            self.score_data['code_snippets'] = val


    def total_code_lines(self, text):
        total = 0
        text = text.replace('```', '\n```')
        lines = text.split('\n')
        ticks_on = False
        for line in lines:
            if line.startswith('```'):
                if ticks_on == False:
                    ticks_on = True
                else:
                    ticks_on = False

            if ticks_on:
                total += 1

        for line in lines:
            if line.startswith('    '):
                total += 1

        return total


    def has_forum_link(self, add=cvar['FORUM_ADD'], forum_url=cvar['FORUM_URL']):
        if re.search(forum_url, self.body):
            self.score += add
            self.score_data['has_forum_link'] = add


    def has_links(self, add=cvar['LINK']):
        total_links = self.total_links(self.body)

        comments = self.data.get('issue_comments')
        if comments:
            for c in comments:
                total_links += self.total_links(c.get('body', ''))

        val = total_links * add
        self.score += val
        if val > 0:
            self.score_data['has_links'] = val


    def total_links(self, text):
        return len(re.findall('http://', text)) + len(re.findall('https://', text))


    def has_issue_reference(self, add=cvar['ISSUE_REFERENCE']):
        total_issue_references = self.total_issue_references(self.body)

        comments = self.data.get('issue_comments')
        if comments:
            for c in comments:
                total_issue_references += self.total_issue_references(c.get('body', ''))

        val = total_issue_references * add
        self.score += val
        if val > 0:
            self.score_data['has_issue_reference'] = val


    def total_issue_references(self, text):
        return len(re.findall(r'#\d+', text))


