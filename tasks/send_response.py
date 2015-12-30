import util
import github_api
from config.config import CONFIG_VARS as cvar


def submit_issue_response(repo_username, repo_id, number, action_type, message_type, custom_message):
    data = {
        'number': number,
        'action_type': action_type,
        'message_type': message_type,
        'custom_message': custom_message
    }

    try:
        issue = github_api.fetch_issue(repo_username, repo_id, number)
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

        elif message_type == 'feature':
            github_api.add_issue_labels(repo_username, repo_id, number, [cvar['FEATURE_REQUEST_LABEL']], issue=issue)
            msg = util.get_template('FEATURE_REQUEST_TEMPLATE', context)

        elif message_type == 'no_reply':
            msg = util.get_template('CLOSING_NOREPLY_TEMPLATE', context)

        elif message_type == 'pr_close':
            msg = util.get_template('CLOSE_PULL_REQUEST_TEMPLATE', context)

        elif message_type == 'custom':
            msg = custom_message

        elif message_type == 'close':
            msg = None

        else:
            data['error'] = 'invalid message_type: %s' % message_type
            return data

        if msg and len(msg.strip()):
            data['created_comment'] = github_api.create_issue_comment(repo_username, repo_id, number, msg)

        if action_type == 'close':
            data['issue_closed'] = github_api.close_issue(repo_username, repo_id, number, issue)

        elif action_type == 'reply':
            github_api.add_issue_labels(repo_username, repo_id, number, [cvar['NEEDS_REPLY_LABEL']], issue=issue)

    except Exception as ex:
        print 'submit_issue_response error, %s: %s' % (number, ex)
        data['error'] = '%s' % ex

    return data
