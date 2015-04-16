from os import getenv as EV

TEMPLATE_VARS = {

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

    'CLOSE_PULL_REQUEST_TEMPLATE': EV('CLOSE_PULL_REQUEST_TEMPLATE'),
}
