from datetime import timedelta, datetime
from config.config import CONFIG_VARS as cvar
import github_api
import send_response
import util


def manage_needs_reply_issue(issue):
    if not issue:
        return

    number = issue.get('number')
    if not number:
        return

    if not has_needs_reply_label(issue):
        return

    issue_events = github_api.fetch_issue_events(number)
    if not issue_events or not isinstance(issue_events, list):
        return

    need_reply_label_added = get_most_recent_datetime_need_reply_label_added(issue_events)
    if not need_reply_label_added:
        return

    issue_comments = github_api.fetch_issue_comments(number)
    if not issue_comments or not isinstance(issue_comments, list):
        return

    most_recent_response = get_most_recent_datetime_creator_response(issue, issue_comments)
    if not most_recent_response:
        return

    print 'Needs reply: %s, label added: %s, most recent response: %s' % (number, need_reply_label_added, most_recent_response)

    if has_replied_since_adding_label(need_reply_label_added, most_recent_response):
        print 'has_replied_since_adding_label, removing label: %s' % number
        return remove_needs_reply_label(number, issue)

    if not has_replied_in_timely_manner(need_reply_label_added):
        print 'not has_replied_in_timely_manner, closing issue: %s' % number
        return close_needs_reply_issue(number)


def has_needs_reply_label(issue):
    if not issue:
        return False
    try:
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

        most_recent = util.get_date(created_str)

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

            created_at = util.get_date(created_str)
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


def remove_needs_reply_label(number, issue):
    try:
        cleaned_labels = []
        old_labels = issue.get('labels')
        for label in old_labels:
            if label.get('name') not in cvar['NEEDS_REPLY_LABELS']:
                cleaned_labels.append(label)
        issue['labels'] = cleaned_labels

        return {
            'remove_needs_reply_label': github_api.remove_issue_labels(number, cvar['NEEDS_REPLY_LABELS'])
        }
    except Exception as ex:
        print 'remove_needs_reply_label error: %s' % ex


def close_needs_reply_issue(number):
    try:
        return {
            'close_needs_reply_issue': send_response.submit_issue_response(number, 'close', 'no_reply', None)
        }
    except Exception as ex:
        print 'close_needs_reply_issue error: %s' % ex


