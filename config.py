from os import getenv as EV

CONFIG_VARS = {

    'DEBUG': True,

    # user/organization name
    'REPO_USERNAME': 'driftyco',
    # name of repo to watch
    'REPO_ID': 'ionic',

    # bot's github username
    'GITHUB_USERNAME': EV('GITHUB_USERNAME'),
    # bot's github password
    'GITHUB_PASSWORD': EV('GITHUB_PASSWORD'),

    # warn after $X inactive days
    'WARN_INACTIVE_AFTER': 80,
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

    'WARNING_TEMPLATE': 'https://raw.githubusercontent.com/driftyco/ionitron-lingo/master/templates/cron/warning.md',
    'CLOSING_TEMPLATE': 'https://raw.githubusercontent.com/driftyco/ionitron-lingo/master/templates/cron/closed.md',


}
