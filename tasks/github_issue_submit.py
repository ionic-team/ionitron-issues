import github_api
import util
from config.config import CONFIG_VARS as cvar


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
    github_api.add_issue_labels(number, [cvar['NEEDS_RESUBMIT_LABEL']], issue=issue)

    return True


def is_valid_issue_opened_source(issue, needs_resubmit_label=cvar['NEEDS_RESUBMIT_LABEL'], test_is_org_member=True):
    if has_content_from_custom_submit_form(issue):
        return True

    if has_needs_resubmit_label(issue, needs_resubmit_label=needs_resubmit_label):
        return True

    if test_is_org_member:
        if github_api.is_org_member(issue['user']['login']):
            return True

    return False


def has_content_from_custom_submit_form(issue):
    body = issue.get('body')
    if body:
        return '<strong>Type</strong>' in issue.get('body', '')
    return False


def has_needs_resubmit_label(issue, needs_resubmit_label=cvar['NEEDS_RESUBMIT_LABEL']):
    labels = issue.get('labels', [])
    for label in labels:
        if label.get('name') == needs_resubmit_label:
            return True
    return False


def remove_flag_if_submitted_through_github(issue):
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

    if not has_needs_resubmit_label(issue):
        return False

    github_api.remove_issue_labels(number, [cvar['NEEDS_RESUBMIT_LABEL']], issue=issue)
    github_api.delete_automated_issue_comments(number)

    return True

