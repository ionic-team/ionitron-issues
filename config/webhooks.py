from os import getenv as EV


WEBHOOK_VARS = {
    'RESUBMIT_TEMPLATE': EV('RESUBMIT_TEMPLATE'),
    'NEEDS_RESUBMIT_LABEL': 'ionitron:please resubmit',
}
