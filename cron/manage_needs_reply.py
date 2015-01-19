
from datetime import timedelta, datetime
from cron.network import fetch
from cron.issue import submit_issue_response
from config.config import CONFIG_VARS as cvar


def manage_needs_reply_issues():
    data = {}

    try:
        data = fetch('issues', '/repos/%s/%s/issues?' % (cvar['REPO_USERNAME'], cvar['REPO_ID']))

        open_issues = data.get('issues')
        if data.get('error') or not open_issues:
            return data

        for issue in open_issues:
            manage_needs_reply_issue(issue)

    except Exception as ex:
        print 'manage_needs_reply_issues error: %s' % ex
        data['error'] = '%s' % ex

    return data


def manage_needs_reply_issue_number(iid):
    try:
        data = fetch('issue', '/repos/%s/%s/issues/%s' % (cvar['REPO_USERNAME'], cvar['REPO_ID'], iid))

        issue = data.get('issue')
        if data.get('error') or not issue:
            print 'manage_needs_reply_issue_number error, %s: %s' % (iid, data.get('error'))
            return data

        return manage_needs_reply_issue(issue)

    except Exception as ex:
        print 'manage_needs_reply_issue_number error: %s' % ex
        data['error'] = '%s' % ex

    return data


def manage_needs_reply_issue(issue):
    if not has_needs_reply_label(issue):
        return

    issue_number = issue.get('number')
    if not issue_number:
        return

    data = fetch('issue_events', '/repos/%s/%s/issues/%s/events' % (cvar['REPO_USERNAME'], cvar['REPO_ID'], issue_number))
    issue_events = data.get('issue_events')
    if data.get('error') or not issue_events:
        return

    need_reply_label_added = get_most_recent_datetime_need_reply_label_added(issue_events)
    if not need_reply_label_added:
        return

    data = fetch('issue_comments', '/repos/%s/%s/issues/%s/comments' % (cvar['REPO_USERNAME'], cvar['REPO_ID'], issue_number))
    issue_comments = data.get('issue_comments')
    if data.get('error') or not issue_comments:
        return

    most_recent_response = get_most_recent_datetime_creator_response(issue, issue_comments)
    if not most_recent_response:
        return

    print 'Needs reply: %s, label added: %s, most recent response: %s' % (issue_number, need_reply_label_added, most_recent_response)

    if has_replied_since_adding_label(need_reply_label_added, most_recent_response):
        print 'has_replied_since_adding_label, removing label: %s' % issue_number
        return remove_needs_reply_label(issue_number)

    if not has_replied_in_timely_manner(need_reply_label_added):
        print 'not has_replied_in_timely_manner, closing issue: %s' % issue_number
        return close_needs_reply_issue(issue_number)


def has_needs_reply_label(issue):
    try:
        if not issue:
            return False

        labels = issue.get('labels')
        if not labels or not len(labels):
            return False

        has_needs_reply_label = False
        for label in labels:
            for needs_reply_label_name in cvar['NEEDS_REPLY_LABELS']:
                if needs_reply_label_name == label.get('name'):
                    return True

    except Exception as ex:
        print 'has_needs_reply_label error: %s' % ex

    return False


def get_most_recent_datetime_need_reply_label_added(events):
    try:
        most_recent = datetime(2000, 1, 1)
        has_recent = False

        if not events or not len(events):
            return

        for event in events:
            event_type = event.get('event')
            if event_type != 'labeled':
                continue

            label = event.get('label')
            if not label:
                continue

            label_name = label.get('name')
            if not label_name:
                continue

            is_needs_reply_label = False
            for needs_reply_label_name in cvar['NEEDS_REPLY_LABELS']:
                if needs_reply_label_name == label.get('name'):
                    is_needs_reply_label = True

            if not is_needs_reply_label:
                continue

            created_str = event.get('created_at')
            if not created_str:
                continue

            created_at = datetime.strptime(created_str, '%Y-%m-%dT%H:%M:%SZ')
            if created_at > most_recent:
                has_recent = True
                most_recent = created_at


        if has_recent:
            return most_recent

    except Exception as ex:
        print 'get_most_recent_datetime_need_reply_label_added error: %s' % ex


def get_most_recent_datetime_creator_response(issue, comments):
    try:
        if not issue:
            return

        creator = issue.get('user')
        if not creator:
            return

        creator_login = creator.get('login')
        if not creator_login:
            return

        created_str = issue.get('created_at')
        if not created_str:
            return

        most_recent = datetime.strptime(created_str, '%Y-%m-%dT%H:%M:%SZ')

        if not comments or not len(comments):
            return most_recent

        for comment in comments:
            comment_user = comment.get('user')
            if not comment_user:
                continue

            comment_login = comment_user.get('login')
            if comment_login != creator_login:
                continue

            created_str = comment.get('created_at')
            if not created_str:
                continue

            created_at = datetime.strptime(created_str, '%Y-%m-%dT%H:%M:%SZ')
            if created_at > most_recent:
                most_recent = created_at

        return most_recent

    except Exception as ex:
        print 'get_most_recent_datetime_creator_comment error: %s' % ex


def has_replied_since_adding_label(need_reply_label_added, most_recent_response):
    return most_recent_response >= need_reply_label_added


def has_replied_in_timely_manner(need_reply_label_added, now=datetime.now(), close_no_reply_after=cvar['CLOSE_NOREPLY_AFTER']):
    not_cool_date = need_reply_label_added + timedelta(days=close_no_reply_after)
    return now < not_cool_date


def remove_needs_reply_label(iid):
    try:
        gh = github3.login(token=cvar['GITHUB_ACCESS_TOKEN'])
        repo = gh.repository(cvar['REPO_USERNAME'], cvar['REPO_ID'])
        issue = repo.issue(number=int(iid))
        if not issue or not issue.labels:
            return

        for label in issue.labels:
            for needs_reply_label_name in cvar['NEEDS_REPLY_LABELS']:
                if label.name == needs_reply_label_name:
                    issue.remove_label(label)

    except Exception as ex:
        print 'remove_needs_reply_label error: %s' % ex


def close_needs_reply_issue(iid):
    try:
        return submit_issue_response(iid, 'close', 'no_reply', None)

    except Exception as ex:
        print 'close_needs_reply_issue error: %s' % ex


