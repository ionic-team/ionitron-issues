from datetime import timedelta, datetime
from config.config import CONFIG_VARS as cvar
import github_api
import send_response
import util


def manage_old_issue(issue):
    if not issue:
        return

    number = issue.get('number')
    if not number:
        return

    if is_closed(issue):
        return

    if is_pull_request(issue):
        return

    updated_str = issue.get('updated_at')
    if not updated_str:
        return

    updated_at = util.get_date(updated_str)
    if not is_old_issue(updated_at):
        return

    if has_labels_preventing_close(issue):
        return

    if has_comments_preventing_close(issue):
        return

    if has_assignee_preventing_close(issue):
        return

    if github_api.is_org_member(issue['user']['login']):
        return

    if cvar['IGNORE_REFERENCED'] is False:
        issue_events = github_api.fetch_issue_events(number)
        if has_events_preventing_close(issue_events):
            return

    return close_old_issue(number, issue)


def is_closed(issue):
    return issue.get('closed_at') is not None


def is_pull_request(issue):
    return issue.get('pull_request') is not None


def has_milestone(issue):
    return issue.get('milestone') is not None


def is_old_issue(updated_at, close_inactive_after=cvar['CLOSE_INACTIVE_AFTER'], now=datetime.now()):
    is_old_date = updated_at + timedelta(days=close_inactive_after)
    return now > is_old_date


def has_labels_preventing_close(issue, do_not_close_labels=cvar['LABEL_BLACKLIST']):
    labels = issue.get('labels')
    if labels:
        for label in labels:
            for do_not_close_label in do_not_close_labels:
                if label.get('name') == do_not_close_label:
                    return True

    return False


def has_comments_preventing_close(issue, max_comments=cvar['MAX_COMMENTS']):
    comments = issue.get('comments')
    if not comments:
        return False

    return comments > max_comments


def has_assignee_preventing_close(issue):
    assignee = issue.get('assignee')
    if assignee:
        return assignee.get('login') is not None
    return False


def is_org_member(user_orgs, org_login=cvar['REPO_USERNAME']):
    if user_orgs:
        for user_org in user_orgs:
            if user_org.get('login') == org_login:
                return True

    return False


def has_events_preventing_close(issue_events):
    if issue_events:
        for issue_event in issue_events:
            if issue_event.get('event') == 'referenced':
                return True

    return False


def close_old_issue(number, issue):
    context = {
        'issue': issue,
        'user': issue.get('user')
    }
    comment = util.get_template('CLOSING_TEMPLATE', context)

    github_api.close_issue(number, issue, remove_labels=cvar['NEEDS_REPLY_LABELS'])
    github_api.create_issue_comment(number, comment)

    return {
        'closed_old_issue': True
    }

