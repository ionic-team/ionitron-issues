from os import getenv as EV
from .score import SCORE_VARS

CONFIG_VARS = {

    # bot will only execute actions if set to False
    'DEBUG': EV('DEBUG') != 'false',

    # user/organization name
    'REPO_USERNAME': 'driftyco', #EV('REPO_USERNAME'),

    # name of repo to watch
    'REPO_ID': 'ionic', #EV('REPO_ID'),

    # bot's github username
    'GITHUB_USERNAME': EV('GITHUB_USERNAME'),

    # bot's github access token
    'GITHUB_ACCESS_TOKEN': EV('GITHUB_ACCESS_TOKEN'),

    # close after $X inactive days
    'CLOSE_INACTIVE_AFTER': 90,

    # close issues that haven't received a reply after $X days
    'CLOSE_NOREPLY_AFTER': 14,

    # labels that indicate more information is required
    'NEEDS_REPLY_LABELS': ['needs reply'],

    'NEEDS_RESUBMIT_LABEL': 'ionitron:please resubmit',

    # ignore issues with these labels
    'LABEL_BLACKLIST': ['in progress', 'ready', 'high priority'],

    # ignore issues with $X+ comments
    'MAX_COMMENTS': 10,

    # label to add when issue is closed
    'ON_CLOSE_LABEL': 'ionitron:closed',

    # whether or not to ignore issues that have been referenced
    'IGNORE_REFERENCED': True,

    # a local or remote template to use for when an issue is closed
    'CLOSING_TEMPLATE': EV('CLOSING_TEMPLATE'),

    # a local or remote template to use for when an issue is closed due to no reply
    'CLOSING_NOREPLY_TEMPLATE': EV('CLOSING_NOREPLY_TEMPLATE'),

    'EXPIRE_TEMPLATE': EV('EXPIRE_TEMPLATE'),

    'FORUM_TEMPLATE': EV('FORUM_TEMPLATE'),

    'INAPPLICABLE_TEMPLATE': EV('INAPPLICABLE_TEMPLATE'),

    'MORE_TEMPLATE': EV('MORE_TEMPLATE'),

    'RESUBMIT_TEMPLATE': EV('RESUBMIT_TEMPLATE'),

    'FEATURE_REQUEST_TEMPLATE': EV('FEATURE_REQUEST_TEMPLATE'),
}

CONFIG_VARS.update(SCORE_VARS)
