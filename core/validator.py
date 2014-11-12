import datetime
from config import CONFIG_VARS as cvar


class Issue:

    def __init__(self, issue):
        self.issue = issue

    def is_valid(self, operation):
        self.operation = operation
        return all({
            'not_closed': not self.issue.is_closed(),
            'old_enough': self.is_old_enough(),
            'no_milestone': not self.issue.milestone,
            'low_activity': self.issue.comments <= cvar['MAX_COMMENTS'],
            'labels_valid': self.labels_valid(),
        }.values())

    def is_old_enough(self):
        today = datetime.datetime.now().date()
        if self.operation == 'warn':
            return (today - self.issue.updated_at.date()).days >= cvar['WARN_INACTIVE_AFTER']
        if self.operation == 'close':
            return (today - self.issue.updated_at.date()).days >= cvar['CLOSE_INACTIVE_AFTER']

    def labels_valid(self):
        labels = [l.name for l in self.issue.labels]
        if '*' in cvar['LABEL_WHITELIST']:  # none can be in blacklist
            return len(set(labels).intersection(set(cvar['LABEL_BLACKLIST']))) == 0
        if '*' in cvar['LABEL_BLACKLIST']:  # at least one must be in whitelist
            return len(set(labels).intersection(set(cvar['LABEL_WHITELIST']))) >= 0 
