import datetime
import re
import github3
import requests
from config.config import CONFIG_VARS as cvar


class Issue:

    """
    An abstraction over Github's Issue object.
    Provides two primary public functions:

    issue.warn(msg='../path/to/message_template.md')
      Warns the issue if valid to do so based on the config rules.
      @kwarg msg: local or remote path to the markdown file to use

    issue.close(msg='../path/to/message_template.md')
      Warns the issue if valid to do so based on the config rules.
      @kwarg msg: local or remote path to the markdown file to use
    """

    def __init__(self, issue):
        self.issue = issue

    def close(self, **kwargs):

        # close because issue is too old
        if kwargs['reason'] == 'old':
            if self.is_valid('close'):
                if cvar['DEBUG'] is False:
                    self.issue.close()
                    self.issue.create_comment(kwargs['msg'])
                    if cvar['ON_CLOSE_LABEL']:
                        self.issue.add_labels(cvar['ON_CLOSE_LABEL'])
                return self.issue.number
            return None

        # close because issue has not received a reply
        if kwargs['reason'] == 'noreply':
            if self.is_valid('close_noreply'):
                if cvar['DEBUG'] is False:
                    self.issue.close()
                    msg = re.sub(r'<%=.*%>', str(cvar['CLOSE_NOREPLY_AFTER']), kwargs['msg'])
                    self.issue.create_comment(msg)
                    if cvar['ON_CLOSE_LABEL']:
                        self.issue.add_labels(cvar['ON_CLOSE_LABEL'])
                return self.issue.number
            return None

    def warn(self, **kwargs):
        if self.is_valid('warn'):

            if cvar['DEBUG'] is False:
                msg = re.sub(r'<%=.*%>', self.issue.user.login, kwargs['msg'])
                self.issue.create_comment(msg)
                if cvar['ON_WARN_LABEL']:
                    self.issue.add_labels(cvar['ON_WARN_LABEL'])

            return self.issue.number

        return None

    def is_valid(self, operation):
        self.operation = operation
        return all({
            'not_closed': not self.issue.is_closed(),
            'old_enough': self.is_old_enough(),
            'no_milestone': not self.issue.milestone,
            'labels_valid': self.labels_valid(),
            'comments_valid': self.comments_valid(),
            'organizations_valid': self.organizations_valid(),
            'references_valid': self.references_valid(),
            'not_pr': self.issue.pull_request is None,
        }.values())

    def is_old_enough(self):
        today = datetime.datetime.now().date()

        if self.operation == 'warn':
            return (today - self.issue.updated_at.date()).days >= cvar['WARN_INACTIVE_AFTER']

        # Adding a warning will update the issue, so updated_at cannot be used
        if self.operation == 'close':
            diff = cvar['CLOSE_INACTIVE_AFTER'] - cvar['WARN_INACTIVE_AFTER']
            return (today - self.issue.updated_at.date()).days >= diff

    def labels_valid(self):

        labels = []

        if hasattr(self.issue, 'labels'):
            labels = [l.name for l in self.issue.labels]

        # Do not double warn issus
        if self.operation == 'warn' and cvar['ON_WARN_LABEL'] in labels:
            return False

        # Ensure warning has been added if closing old issue
        if self.operation == 'close' and cvar['ON_WARN_LABEL'] not in labels:
            return False

        # None can be in blacklist
        if '*' in cvar['LABEL_WHITELIST']:
            return len(set(labels).intersection(set(cvar['LABEL_BLACKLIST']))) == 0

        # At least one must be in whitelist
        if '*' in cvar['LABEL_BLACKLIST']:
            return len(set(labels).intersection(set(cvar['LABEL_WHITELIST']))) >= 0

    def comments_valid(self):

        # Total comments cannot exceed MAX_COMMENTS
        if hasattr(self.issue, 'comments'):
            if self.issue.comments > cvar['MAX_COMMENTS']:
                return False

        # The last comment must be from the bot user
        if self.operation == 'close':
            comments = list(self.issue.iter_comments())
            if len(comments) == 0:
                return False
            return comments[-1].user.login == cvar['GITHUB_USERNAME']

        return True

    def organizations_valid(self):

        op_orgs = list(self.issue.user.iter_orgs())

        if len(op_orgs) > 0:
            return len(set(op_orgs).intersection(set(cvar['ORGANIZATION_BLACKLIST']))) == 0

        return True

    def references_valid(self):

        if cvar['IGNORE_REFERENCED'] is False:
            return True

        # if any events are referenced events, return False
        events = list(self.issue.iter_events())
        if len(events) > 0:
            return not any([e.event == 'referenced' for e in events])

        return True

    def needs_reply(self):

        # issue must have needs reply label
        if hasattr(self.issue, 'labels'):
            labels = [l.name for l in self.issue.labels]
            if len(set(labels).intersection(set(cvar['NEEDS_REPLY_LABELS']))) >= 1:

                # get timestamp for needs reply label
                events = list(self.issue.iter_events())
                for e in events:
                    ed = e.to_json()
                    if e.event == 'labeled' and ed['label']['name'] in cvar['NEEDS_REPLY_LABELS']:

                        # comments must be older than label_time, unless from user who added needs reply label
                        label_time = datetime.datetime.strptime(ed['created_at'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=None)
                        comments = list(self.issue.iter_comments())
                        return not any([c for c in comments if c.created_at.replace(tzinfo=None) > label_time and c.user.login != e.actor.login])

        return False


def close_old_issues():

    gh = github3.login(token=cvar['GITHUB_ACCESS_TOKEN'])
    repo = gh.repository(cvar['REPO_USERNAME'], cvar['REPO_ID'])
    issues = repo.iter_issues()

    try:  # Read message templates from remote URL
        msg = requests.get(cvar['CLOSING_TEMPLATE']).text
    except:  # Read from local file
        msg = open(cvar['CLOSING_TEMPLATE']).read()



    closed = [Issue(i).close(msg=msg, reason='old') for i in issues]

    print 'Old Issues Closed: '
    print filter(lambda x: x is not None, closed)


def warn_old_issues():

    gh = github3.login(token=cvar['GITHUB_ACCESS_TOKEN'])

    repo = gh.repository(cvar['REPO_USERNAME'], cvar['REPO_ID'])
    issues = repo.iter_issues()

    try:  # Read from remote URL
        warning_msg = requests.get(cvar['WARNING_TEMPLATE']).text
    except:  # Read from local file
        warning_msg = open(cvar['WARNING_TEMPLATE']).read()

    warned = [Issue(i).warn(msg=warning_msg) for i in issues]

    print "Old Issues Warned: "
    print filter(lambda x: x is not None, warned)


def submit_issue_response(iid, action_type, message_type, custom_message):
    gh = github3.login(token=cvar['GITHUB_ACCESS_TOKEN'])
    repo = gh.repository(cvar['REPO_USERNAME'], cvar['REPO_ID'])
    data = {
        'action_type': action_type,
        'iid': iid,
        'message_type': message_type,
        'custom_message': custom_message
    }

    try:
        issue = repo.issue(number=iid)
        if not issue:
            data['error'] = 'could not find issue %s' % iid
            return data

        user_data = { 'user': { 'login': issue.user.login }}

        if message_type == 'expire':
            issue.create_comment(get_template('EXPIRE_TEMPLATE', user_data))

        elif message_type == 'forum':
            issue.create_comment(get_template('FORUM_TEMPLATE', user_data))

        elif message_type == 'inapplicable':
            issue.create_comment(get_template('INAPPLICABLE_TEMPLATE', user_data))

        elif message_type == 'more':
            issue.create_comment(get_template('MORE_TEMPLATE', user_data))

        elif message_type == 'no_reply':
            issue.create_comment(get_template('CLOSING_NOREPLY_TEMPLATE', user_data))

        elif message_type == 'custom' and custom_message:
            issue.create_comment(custom_message)

        else:
            data['error'] = 'invalid message_type %s' % message_type
            return data

        if action_type == 'close':
            issue.close()
            if issue.labels:
                for label in issue.labels:
                    for needs_reply_label_name in cvar['NEEDS_REPLY_LABELS']:
                        if label.name == needs_reply_label_name:
                            issue.remove_label(label)
            data['issue_closed'] = True

    except Exception as ex:
        print 'submit_issue_response error, %s: %s' % (iid, ex)
        data['error'] = '%s' % ex

    return data


def get_template(key, data):
    try:  # Read message templates from remote URL
        msg = requests.get(cvar[key]).text

        from jinja2 import Environment, PackageLoader, Template
        env = Environment(loader=PackageLoader('main', 'templates'))
        env.variable_start_string = '<%='
        env.variable_end_string = '%>'
        template = env.from_string(msg)
        return template.render(data)

    except Exception as ex:
        print 'get_template %s' % ex


def test_api_access():
    try:
        url_vars = (cvar['REPO_USERNAME'], cvar['REPO_ID'])
        url = 'https://api.github.com/repos/%s/%s/stats/contributors' % url_vars
        auth = (cvar['GITHUB_ACCESS_TOKEN'], '')
        return requests.get(url, auth=auth).json()
    except Exception as ex:
        print ex
        return { 'error': '%s' % ex }

