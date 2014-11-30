import datetime
import re
from config import CONFIG_VARS as cvar


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
        if self.is_valid('close'):

            if cvar['DEBUG'] is False:
                self.issue.close()
                self.issue.create_comment(kwargs['msg'])
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

        # Ensure warning has been added if closing
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
