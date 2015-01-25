import datetime
import re
from config.config import CONFIG_VARS as cvar
import util


class ScoreCalculator():
    """
    An abstraction over a github issue object used to calculate a score.
    """

    def __init__(self, number=None, data={}):
        self.number = number
        self.data = data

        self.score = 0
        self.number_of_comments = 0
        self.score_data = {}

        self.issue = self.data.get('issue', {})
        self.title = self.issue.get('title')
        if not self.title:
            self.title = ''
        self.body = self.issue.get('body')
        if not self.body:
            self.body = ''
        self.user = self.issue.get('user', {})
        self.login = self.user.get('login', '') or ''
        self.avatar = self.user.get('avatar_url', '') or ''

        self.assignee = ''
        assignee = self.issue.get('assignee')
        if assignee:
            self.assignee = assignee.get('login', '') or ''

        self.created_at = util.get_date(self.issue.get('created_at'))
        self.updated_at = util.get_date(self.issue.get('updated_at'))

        comments = self.data.get('issue_comments')
        if comments:
            self.number_of_comments = len(comments)

        self.org_members = self.data.get('org_members', [])


    def load_scores(self):
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
        self.short_title_text()
        self.short_body_text()
        self.every_x_characters_in_body()
        self.code_demos()
        self.daily_decay_since_creation()
        self.daily_decay_since_last_update()
        self.awaiting_reply()
        self.each_unique_commenter()
        self.each_comment()
        self.code_snippets()
        self.images()
        self.forum_links()
        self.links()
        self.issue_references()

        return self.score

    def to_dict(self):
        return {
            'number': self.number,
            'score': self.score,
            'title': self.title,
            'comments': self.number_of_comments,
            'assignee': self.assignee,
            'created': self.created_at.isoformat(),
            'updated': self.updated_at.isoformat(),
            'username': self.login,
            'avatar': self.avatar,
            'score_data': self.score_data,
        }


    ### Repo / Organization

    def core_team_member(self, add=cvar['CORE_TEAM']):
        if self.login in self.org_members:
            self.score += add
            self.score_data['core_team_member'] = add


    def each_contribution(self, add=cvar['CONTRIBUTION'], max_contribution=cvar['CONTRIBUTION_MAX']):
        contributors = self.data.get('contributors')
        if not contributors or not isinstance(contributors, list):
            return
        contrib = [c for c in contributors if self.login == c.get('login')]
        if contrib and len(contrib):
            contributions = contrib[0].get('contributions')
            if contributions:
                val = int(min(max_contribution, (int(contributions)*add)))
                self.score += val
                if val > 0:
                    self.score_data['each_contribution'] = val



    ### Issue

    def short_title_text(self, subtract=cvar['SHORT_TITLE_TEXT_SUBTRACT'], short_title_text_length=cvar['SHORT_TITLE_TEXT_LENGTH']):
        if len(self.title) < short_title_text_length:
            self.score -= subtract
            self.score_data['short_title_text'] = subtract * -1


    def short_body_text(self, subtract=cvar['SHORT_BODY_TEXT_SUBTRACT'], short_body_text_length=cvar['SHORT_BODY_TEXT_LENGTH']):
        if len(self.body) < short_body_text_length:
            self.score -= subtract
            self.score_data['short_body_text'] = subtract * -1


    def every_x_characters_in_body(self, add=cvar['BODY_CHAR_ADD'], x=cvar['BODY_CHAR_X']):
        val = self.every_x_chacters(self.body, add, x)
        if val > 0:
            self.score += val
            self.score_data['every_x_characters_in_body'] = val


    def every_x_characters_in_comments(self, add=cvar['COMMENT_CHAR_ADD'], x=cvar['COMMENT_CHAR_X']):
        val = 0
        comments = self.data.get('issue_comments')
        if comments:
            for c in comments:
                comment_login = c.get('user', {}).get('login')
                if comment_login and comment_login not in self.org_members:
                    val += self.every_x_chacters(c.get('body'), add, x)
        if val > 0:
            self.score += val
            self.score_data['every_x_characters_in_comments'] = val


    def every_x_chacters(self, text, add, x):
        if text:
            return int(float(len(text)) / float(x)) * add
        return 0


    def code_demos(self, add=cvar['DEMO'], demo_domains=cvar['DEMO_DOMAINS']):
        val = 0
        for demo_domain in demo_domains:
            val += len(re.findall(demo_domain, self.body))
        val = val * add
        self.score += val
        if val > 0:
            self.score_data['code_demos'] = val


    def daily_decay_since_creation(self, exp=cvar['CREATION_DECAY_EXP'], start=cvar['CREATED_START'], now=datetime.datetime.now()):
        if not self.created_at:
            return
        days_since_creation = abs((now - self.created_at).days)
        val = int(float(start) - min((float(days_since_creation)**exp), start))
        self.score += val
        if val > 0:
            self.score_data['daily_decay_since_creation'] = val
        return {
            'days_since_creation': days_since_creation,
            'exp': exp,
            'start': start,
            'score': val
        }


    def daily_decay_since_last_update(self, exp=cvar['LAST_UPDATE_DECAY_EXP'], start=cvar['UPDATE_START'], now=datetime.datetime.now()):
        if not self.updated_at:
            return
        days_since_update = abs((now - self.updated_at).days)
        val = int(float(start) - min((float(days_since_update)**exp), start))
        self.score += val
        if val > 0:
            self.score_data['daily_decay_since_last_update'] = val
        return {
            'days_since_update': days_since_update,
            'exp': exp,
            'start': start,
            'score': val
        }


    def awaiting_reply(self, subtract=cvar['AWAITING_REPLY']):
        issue_labels = self.issue.get('labels')
        if issue_labels:
            label_set = set([l['name'] for l in issue_labels])
            if cvar['NEEDS_REPLY_LABEL'] in label_set:
                self.score -= subtract
                self.score_data['awaiting_reply'] = subtract * -1


    def each_unique_commenter(self, add=cvar['UNIQUE_USER_COMMENT']):
        comments = self.data.get('issue_comments')
        if not comments:
            return

        commenters = []
        for comment in comments:
            comment_login = comment.get('user', {}).get('login')
            if comment_login and comment_login not in commenters and comment_login not in self.org_members:
                if comment_login != self.login:
                    commenters.append(comment_login)

        val = len(commenters) * add
        if val > 0:
            self.score += val
            self.score_data['each_unique_commenter'] = val


    def each_comment(self, add=cvar['COMMENT']):
        val = len(self.data.get('issue_comments', [])) * add
        if val > 0:
            self.score += val
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

    def images(self, add=cvar['IMAGE']):
        all_images = self.get_images(self.body)

        comments = self.data.get('issue_comments')
        if comments:
            for c in comments:
                all_images += self.get_images(c.get('body', ''))

        images = []
        for image in all_images:
            if image not in images:
                images.append(image)

        val = len(images) * add
        self.score += val
        if val > 0:
            self.score_data['images'] = val


    def get_images(self, text):
        images = []
        links = self.get_links(text)
        for link in links:
            if self.is_image(link) and link not in images:
                images.append(link)
        return images


    def forum_links(self, add=cvar['FORUM_LINK'], forum_url=cvar['FORUM_URL']):
        all_links = self.get_links(self.body)

        comments = self.data.get('issue_comments')
        if comments:
            for c in comments:
                all_links += self.get_links(c.get('body', ''))

        links = []
        for link in all_links:
            if link not in links:
                if 'forum.ionicframework.com' in link:
                    links.append(link)

        val = len(links) * add
        self.score += val
        if val > 0:
            self.score_data['forum_links'] = val


    def links(self, add=cvar['LINK']):
        all_links = self.get_links(self.body)

        comments = self.data.get('issue_comments')
        if comments:
            for c in comments:
                all_links += self.get_links(c.get('body', ''))

        links = []
        for link in all_links:
            if link not in links:
                if not self.is_image(link):
                    if 'forum.ionicframework.com' not in link:
                        links.append(link)

        val = len(links) * add
        self.score += val
        if val > 0:
            self.score_data['links'] = val


    def get_links(self, text):
        links = []
        words = self.get_words(text)
        for word in words:
            if word and len(word) > 10:
                if word.startswith('http://') or word.startswith('https://'):
                    if word not in links:
                        links.append(word)
        return links


    def issue_references(self, add=cvar['ISSUE_REFERENCE']):
        all_issue_references = self.get_issue_references(self.body)

        comments = self.data.get('issue_comments')
        if comments:
            for c in comments:
                all_issue_references += self.get_issue_references(c.get('body', ''))

        references = []
        for reference in all_issue_references:
            if reference not in references:
                references.append(reference)

        val = len(references) * add
        self.score += val
        if val > 0:
            self.score_data['issue_references'] = val


    def get_issue_references(self, text):
        words = self.get_words(text)
        references = []
        for word in words:
            word = word.replace('.', '')
            if re.findall(r'#\d+', word):
                if word not in references:
                    references.append(word)
        return references


    def get_words(self, text):
        if text is None or text == '':
            return []

        delimiters = ['\n', '\t', ' ', '"', "'", '\(', '\)', '\[', '\]']
        return re.split('|'.join(delimiters), text.lower())


    def is_image(self, link):
        link = link.lower()
        return link.startswith('http') and (link.endswith('.png') or link.endswith('.jpg') or link.endswith('.jpeg') or link.endswith('.gif') or link.endswith('.svg') or link.endswith('.webp'))

