import util
import github_api
from config.config import CONFIG_VARS as cvar


def submit_issue_response(number, action_type, message_type, custom_message):
    data = {
        'number': number,
        'action_type': action_type,
        'message_type': message_type,
        'custom_message': custom_message
    }

    try:
        issue = github_api.fetch_issue(number)
        if not issue or issue.get('error'):
            data['error'] = 'could not find issue %s' % number
            return data

        context = {
            'issue': issue,
            'user': issue.get('user')
        }
        msg = None

        if message_type == 'expire':
            msg = util.get_template('EXPIRE_TEMPLATE', context)

        elif message_type == 'forum':
            msg = util.get_template('FORUM_TEMPLATE', context)

        elif message_type == 'inapplicable':
            msg = util.get_template('INAPPLICABLE_TEMPLATE', context)

        elif message_type == 'more':
            msg = util.get_template('MORE_TEMPLATE', context)

        elif message_type == 'no_reply':
            msg = util.get_template('CLOSING_NOREPLY_TEMPLATE', context)

        elif message_type == 'custom' and custom_message:
            msg = custom_message

        else:
            data['error'] = 'invalid message_type: %s' % message_type
            return data

        data['created_comment'] = github_api.create_issue_comment(number, msg)

        if action_type == 'close':
            data['issue_closed'] = github_api.close_issue(number, issue, remove_labels=cvar['NEEDS_REPLY_LABELS'])

    except Exception as ex:
        print 'submit_issue_response error, %s: %s' % (number, ex)
        data['error'] = '%s' % ex

    return data

