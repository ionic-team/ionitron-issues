from os import getenv as EV


CRON_VARS = {
    # warn after $X inactive days
    'WARN_INACTIVE_AFTER': 83,
    # close after $X inactive days
    'CLOSE_INACTIVE_AFTER': 90,
    # close issues that haven't received a reply after $X days
    'CLOSE_NOREPLY_AFTER': 30,
    # labels that indicate more information is required
    'NEEDS_REPLY_LABELS': ['needs reply'],
    # ignore issues with $X+ comments
    'MAX_COMMENTS': 10,
    # only take action on issues with these labels
    'LABEL_WHITELIST': ['*'],
    # ignore issues with these labels
    'LABEL_BLACKLIST': ['in progress', 'ready'],
    # label to add when issue is warned
    'ON_WARN_LABEL': 'ionitron:warned',
    # label to add when issue is closed
    'ON_CLOSE_LABEL': 'ionitron:closed',
    # do not take action on if OP is a member of one of these organizations
    'ORGANIZATION_BLACKLIST': ['driftyco'],
    # whether or not to ignore issues that have been referenced
    'IGNORE_REFERENCED': True,
    # a local or remote template to use for the warning message
    'WARNING_TEMPLATE': EV('WARNING_TEMPLATE'),
    # a local or remote template to use for when an issue is closed
    'CLOSING_TEMPLATE': EV('CLOSING_TEMPLATE'),
    # a local or remote template to use for when an issue is closed due to no reply
    'CLOSING_NOREPLY_TEMPLATE': EV('CLOSING_NOREPLY_TEMPLATE'),
}
