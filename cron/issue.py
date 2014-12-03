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
        }.values())

    def is_old_enough(self):
        today = datetime.datetime.now().date()

        if self.operation == 'warn':
            return (today - self.issue.updated_at.date()).days >= cvar['WARN_INACTIVE_AFTER']

        # Adding a warning will update the issue, so updated_at cannot be used
        if self.operation == 'close':
            diff = cvar['CLOSE_INACTIVE_AFTER'] - cvar['WARN_INACTIVE_AFTER']
            return (today - self.issue.updated_at.date()).days >= diff

        if self.operation == 'close_noreply':
            return (today - self.issue.updated_at.date()).days >= cvar['CLOSE_NOREPLY_AFTER']

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

        # Ensure needs reply label has been added if closing unreplied issue
        if self.operation == 'close_noreply' and not self.needs_reply():
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
