from os import getenv as EV

CONFIG_VARS = {

    'DEBUG': True,

    'REPO_USERNAME': 'driftyco',               # user/organization name
    'REPO_ID': 'ionic',                        # name of repo to watch

    'GITHUB_USERNAME': EV('GITHUB_USERNAME'),  # bot's github username
    'GITHUB_PASSWORD': EV('GITHUB_PASSWORD'),  # bot's github password

    'WARN_INACTIVE_AFTER': 80,                 # warn after $X inactive days
    'CLOSE_INACTIVE_AFTER': 87,                # close after $X inactive days

    'MAX_COMMENTS': 10,                        # ignore issues with $X+ comments

    'LABEL_WHITELIST': ['*'],                  # only take action on issues with these labels
    'LABEL_BLACKLIST': ['in progress'],        # ignore issues with these labels

    'ON_WARN_LABEL': 'ionitron:warned',        # label to add when issue is warned
    'ON_CLOSE_LABEL': 'ionitron:closed',       # label to add when issue is closed

    'WARNING_TEMPLATE': 'https://raw.githubusercontent.com/driftyco/ionitron-lingo/master/templates/cron/warning.md',
    'CLOSING_TEMPLATE': 'https://raw.githubusercontent.com/driftyco/ionitron-lingo/master/templates/cron/closed.md',


}
