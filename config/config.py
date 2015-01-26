from os import getenv as EV
from .score import SCORE_VARS
from .templates import TEMPLATE_VARS

CONFIG_VARS = {

    # bot will only execute actions if set to False
    'DEBUG': EV('DEBUG') != 'false',

    # user/organization name
    'REPO_USERNAME': EV('REPO_USERNAME'),

    # name of repo to watch
    'REPO_ID': EV('REPO_ID'),

    # bot's github username
    'GITHUB_USERNAME': EV('GITHUB_USERNAME'),

    # bot's github access token
    'GITHUB_ACCESS_TOKEN': EV('GITHUB_ACCESS_TOKEN'),

    # close after $X inactive days
    'CLOSE_INACTIVE_AFTER': 90,

    # close issues that haven't received a reply after $X days
    'CLOSE_NOREPLY_AFTER': 14,

    # do not close issues with $X+ comments
    'DO_NOT_CLOSE_MIN_COMMENTS': 10,

    # whether or not to ignore issues that have been referenced
    'DO_NOT_CLOSE_WHEN_REFERENCED': True,

    # do not close issues that have these labels
    'DO_NOT_CLOSE_LABELS': ['in progress', 'ready', 'high priority'],

    # label to add when issue is closed
    'ON_CLOSE_LABEL': 'ionitron:closed',

    # label saying its a feature request
    'FEATURE_REQUEST_LABEL': 'feature',

    # label that indicates we asked a question and need a response
    'NEEDS_REPLY_LABEL': 'needs reply',

    # label to add when requesting to resubmit through the custom form
    'NEEDS_RESUBMIT_LABEL': 'ionitron:please resubmit',

    # labels to automatically remove when replying/closing
    'AUTO_REMOVE_LABELS': ['ready', 'in progress', 'ionitron:warned'],
}

CONFIG_VARS.update(SCORE_VARS)
CONFIG_VARS.update(TEMPLATE_VARS)
