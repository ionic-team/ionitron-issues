from os import getenv as EV

CONFIG_VARS = {

    ########################################
    # General
    ########################################

    # bot will only execute actions if set to False
    'DEBUG': True,
    # user/organization name
    'REPO_USERNAME': 'driftyco',
    # name of repo to watch
    'REPO_ID': 'ionic',
    # bot's github username
    'GITHUB_USERNAME': EV('GITHUB_USERNAME'),
    # bot's github password
    'GITHUB_PASSWORD': EV('GITHUB_PASSWORD'),


    ########################################
    # Cron - warn/remove issues
    ########################################

    # warn after $X inactive days
    'WARN_INACTIVE_AFTER': 73,
    # close after $X inactive days
    'CLOSE_INACTIVE_AFTER': 87,
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
    # a local or remote template to use for the warning message
    'WARNING_TEMPLATE': EV('WARNING_TEMPLATE'),
    # a local or remote template to use for when an issue is closed
    'CLOSING_TEMPLATE': EV('CLOSING_TEMPLATE'),

}
