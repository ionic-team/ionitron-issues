from os import getenv as EV
from .cron import CRON_VARS
from .score import SCORE_VARS
from .webhooks import WEBHOOK_VARS

CONFIG_VARS = {

    # bot will only execute actions if set to False
    'DEBUG': True,
    # user/organization name
    'REPO_USERNAME': EV('REPO_USERNAME'),
    # name of repo to watch
    'REPO_ID': EV('REPO_ID'),
    # bot's github username
    'GITHUB_USERNAME': EV('GITHUB_USERNAME'),
    # bot's github password
    'GITHUB_PASSWORD': EV('GITHUB_PASSWORD'),
}

CONFIG_VARS.update(WEBHOOK_VARS)
CONFIG_VARS.update(CRON_VARS)
CONFIG_VARS.update(SCORE_VARS)