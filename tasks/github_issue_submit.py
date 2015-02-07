import github_api
import util
from config.config import CONFIG_VARS as cvar
from datetime import datetime, timedelta


def flag_if_submitted_through_github(issue):
    """
    Flags any issue that is submitted through github's UI, and not the Ionic site.
    Adds a label, as well as a comment, to force the issue through the custom form.
    @return: whether or not the issue was flagged (bool)
    """

    if not issue:
        return False

    number = issue.get('number')
    if not number:
        return False

    user = issue.get('user')
    if not user:
        return False

    if not issue.get('body'):
        return False

    if is_valid_issue_opened_source(issue):
        return False

    context = {
        'issue': issue,
        'user': user
    }
    msg = util.get_template('RESUBMIT_TEMPLATE', context)

    github_api.create_issue_comment(number, msg)

    return True


def is_valid_issue_opened_source(issue, issue_comments=None, needs_resubmit_content_id=cvar['NEEDS_RESUBMIT_CONTENT_ID'], test_is_org_member=True):
    if has_content_from_custom_submit_form(issue):
        return True

    if test_is_org_member:
        if github_api.is_org_member(issue['user']['login']):
            return True

    if has_needs_resubmit_content_id(issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id):
        return True

    return False


def has_content_from_custom_submit_form(issue):
    body = issue.get('body')
    if body:
        return 'is-issue-template' in body
    return False


def has_needs_resubmit_content_id(issue, issue_comments=None, needs_resubmit_content_id=cvar['NEEDS_RESUBMIT_CONTENT_ID']):
    comment = get_needs_resubmit_comment(issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id)
    return not comment is None


def get_needs_resubmit_comment(issue, issue_comments=None, needs_resubmit_content_id=cvar['NEEDS_RESUBMIT_CONTENT_ID']):
    if issue_comments is None:
        issue_comments = github_api.fetch_issue_comments(issue.get('number'))

    if issue_comments and isinstance(issue_comments, list):
        for issue_comment in issue_comments:
            body = issue_comment.get('body')
            if body and needs_resubmit_content_id in body:
                return issue_comment


def remove_flag_if_submitted_through_github(issue, issue_comments=None, is_debug=cvar['DEBUG']):
    """
    Removes the notice flag (automated comments and label) if the issue has been
    resubmitted through the custom form on the Ionic site.
    @param issueNum: the issue number that should be refreshed (string)
    @return: whether or not the flag was removed (bool)
    """

    if not issue:
        return False

    number = issue.get('number')
    if not number:
        return False

    if not has_content_from_custom_submit_form(issue):
        return False

    if not has_needs_resubmit_content_id(issue, issue_comments=issue_comments):
        return False

    if not is_debug:
        github_api.delete_automated_issue_comments(number)

    return True


def remove_flag_if_not_updated(issue, issue_comments=None, needs_resubmit_content_id=cvar['NEEDS_RESUBMIT_CONTENT_ID'], remove_form_resubmit_comment_after=cvar['REMOVE_FORM_RESUBMIT_COMMENT_AFTER'], now=datetime.now(), is_debug=cvar['DEBUG']):
    if not issue:
        return False

    number = issue.get('number')
    if not number:
        return False

    if has_content_from_custom_submit_form(issue):
        return False

    comment = get_needs_resubmit_comment(issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id)
    if comment is None:
        return False

    created_at = util.get_date(comment.get('created_at'))
    if created_at is None:
        return False

    remove_date = created_at + timedelta(days=remove_form_resubmit_comment_after)
    if remove_date > now:
        return False

    if not is_debug:
        github_api.delete_automated_issue_comments(number)

    return True


def remove_flag_when_closed(issue, issue_comments=None, needs_resubmit_content_id=cvar['NEEDS_RESUBMIT_CONTENT_ID'], is_debug=cvar['DEBUG']):
    if not issue:
        return False

    number = issue.get('number')
    if not number:
        return False

    if has_content_from_custom_submit_form(issue):
        return False

    comment = get_needs_resubmit_comment(issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id)
    if comment is None:
        return False

    comment_id = comment.get('id')
    if comment_id is None:
        return False

    if not is_debug:
        github_api.delete_issue_comment(comment_id, number=number)

    return True

