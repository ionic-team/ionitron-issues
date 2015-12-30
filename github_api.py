import requests
import util
from config.config import CONFIG_VARS as cvar
import json

GITHUB_AUTH = (cvar['GITHUB_ACCESS_TOKEN'], '')
GITHUB_API_URL = 'https://api.github.com'


def fetch_open_issues(repo_username, repo_id):
    open_issues = []
    issues = fetch('/repos/%s/%s/issues?' % (repo_username, repo_id), 0)
    if isinstance(issues, list):
        for issue in issues:
            open_issues.append(issue)
    return open_issues


def fetch_issue(repo_username, repo_id, number):
    return fetch('/repos/%s/%s/issues/%s' % (repo_username, repo_id, number))


def fetch_issue_comments(repo_username, repo_id, number):
    return fetch('/repos/%s/%s/issues/%s/comments' % (repo_username, repo_id, number))


def fetch_issue_events(repo_username, repo_id, number):
    return fetch('/repos/%s/%s/issues/%s/events' % (repo_username, repo_id, number))


def fetch_user(login):
    return fetch('/users/%s' % (login), 60*60*24*7)


def fetch_repo_contributors(repo_username, repo_id):
    return fetch('/repos/%s/%s/contributors' % (repo_username, repo_id), 60*60*24*7)


def fetch_org_members_logins(repo_username):
    logins = []
    org = repo_username

    cache_key = '%s:members' % (org)
    cached_data = util.get_cached_data(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        org_members = fetch('/orgs/%s/members' % org, 60*60*24*7)
        if not isinstance(org_members, list):
            logins.append(org)
            util.set_cached_data(cache_key, logins, 60*60*24*7)
            return logins

        for org_member in org_members:
            logins.append(org_member.get('login'))

        org_teams = fetch('/orgs/%s/teams' % org, 60*60*24*7)
        for org_team in org_teams:
            org_team_members = fetch('/teams/%s/members' % (org_team.get('id')), 60*60*24*7)

            for org_team_member in org_team_members:
                team_member_login = org_team_member.get('login')
                if team_member_login not in logins:
                    logins.append(team_member_login)

        if len(logins):
            util.set_cached_data(cache_key, logins, 60*60*24*7)

    except Exception as ex:
        print 'fetch_org_members_logins, %s' % ex

    return logins


def is_org_member(repo_username, login):
    org_member_logins = fetch_org_members_logins(repo_username)
    if isinstance(org_member_logins, list):
        return login in org_member_logins
    return login == repo_username


def fetch(path, expires=60):
    try:
        url = '%s%s' % (GITHUB_API_URL, path)

        if expires > 0:
            cache_key = url
            cached_data = util.get_cached_data(cache_key)

            if cached_data:
                #print 'fetched from cache: %s' % path
                return cached_data

        #print 'fetch: %s' % path

        data = None
        try:
            r = requests.get(url, auth=GITHUB_AUTH)
            if r.status_code == 204:
                data = { 'error': 'no content' }
            elif r.status_code < 204:
                data = r.json()
            else:
                return { 'error': r.text, 'status_code': r.status_code }

        except Exception as ex:
            print 'fetch error, %s:, %s' % (path, ex)
            return { 'error': '%s' % ex, 'fetch': url }

        # Iterate through additional pages of data if available
        has_next = True if 'next' in r.links else False
        while has_next:
            try:
                url = r.links['next']['url']
                r = requests.get(url, auth=GITHUB_AUTH)
                if r.status_code < 204:
                    data += r.json()
                    has_next = True if 'next' in r.links else False
                else:
                    has_next = False
                    data['error'] = r.text
                    return data

            except Exception as ex:
                print 'fetch error, %s:, %s' % (path, ex)
                return { 'error': '%s' % ex, 'next_fetch': url }

        if expires > 0:
            util.set_cached_data(cache_key, data, expires)

        return data

    except Exception as ex:
        print 'fetch_data, %s: %s' % (url, ex)
        return { 'error': '%s' % ex, 'fetch': url }


def create_issue_comment(repo_username, repo_id, number, body):
    if cvar['DEBUG']:
        print 'create_issue_comment, issue %s:\n%s' % (number, body)
        return

    try:
        data = { 'body': body }
        url = '%s/repos/%s/%s/issues/%s/comments' % (GITHUB_API_URL, repo_username, repo_id, number)
        requests.post(url, data=json.dumps(data), auth=GITHUB_AUTH)

    except Exception as ex:
        print 'create_issue_comment, issue %s: %s' % (number, ex)
        return { 'error': '%s' % ex }


def delete_issue_comment(repo_username, repo_id, comment_id, number=None):
    if cvar['DEBUG']:
        print 'delete_issue_comment: %s, issue: %s' % (comment_id, number)
        return

    try:
        url = '%s/repos/%s/%s/issues/comments/%s' % (GITHUB_API_URL, repo_username, repo_id, comment_id)
        requests.delete(url, auth=GITHUB_AUTH)

    except Exception as ex:
        print 'delete_issue_comment, comment_id %s: %s' % (comment_id, ex)
        return { 'error': '%s' % ex }


def delete_automated_issue_comments(repo_username, repo_id, number, comments=None, is_debug=cvar['DEBUG'], automated_login=cvar['GITHUB_USERNAME']):
    try:
        data = {
            'deleted_automated_issue_comments': 0
        }

        if comments is None:
            comments = fetch_issue_comments(repo_username, repo_id, number)

        if comments and isinstance(comments, list):
            for comment in comments:
                comment_id = comment.get('id')
                if comment_id is not None:
                    comment_login = comment.get('user', {}).get('login')
                    if comment_login and comment_login.lower() == automated_login.lower():
                        if not is_debug:
                            delete_issue_comment(repo_username, repo_id, comment_id, number)
                        data['deleted_automated_issue_comments'] += 1

        return data

    except Exception as ex:
        print 'delete_automated_issue_comments, issue %s: %s' % (number, ex)
        return { 'error': '%s' % ex }


def add_issue_labels(repo_username, repo_id, number, add_labels, issue=None, is_debug=cvar['DEBUG']):
    try:
        return issue_edit(repo_username, repo_id, number, add_labels=add_labels, issue=issue, is_debug=is_debug)

    except Exception as ex:
        print 'add_issue_labels, issue %s: %s' % (number, ex)
        return { 'error': '%s' % ex }


def remove_issue_labels(repo_username, repo_id, number, remove_labels, issue=None, is_debug=cvar['DEBUG']):
    try:
        return issue_edit(repo_username, repo_id, number, remove_labels=remove_labels, issue=issue, is_debug=is_debug)

    except Exception as ex:
        print 'remove_issue_labels, issue %s: %s' % (number, ex)
        return { 'error': '%s' % ex }


def close_issue(repo_username, repo_id, number, issue=None, add_labels=[], remove_labels=[], is_debug=cvar['DEBUG']):
    try:
        add_labels.append(cvar['ON_CLOSE_LABEL'])
        remove_labels.append(cvar['NEEDS_REPLY_LABEL'])

        return issue_edit(repo_username, repo_id, number, assignee='', state='closed', milestone='', add_labels=add_labels, remove_labels=remove_labels, issue=issue, is_debug=is_debug)

    except Exception as ex:
        print 'close_issue, issue %s: %s' % (number, ex)
        return { 'error': '%s' % ex }


def issue_edit(repo_username, repo_id, number, title=None, body=None, assignee=None, state=None, milestone=None, add_labels=[], remove_labels=[], issue=None, is_debug=cvar['DEBUG']):
    try:
        remove_labels += cvar['AUTO_REMOVE_LABELS']

        if add_labels is not None or remove_labels is not None:
            if not issue:
                issue = fetch_issue(repo_username, repo_id, number)

            labels = []
            old_labels = issue.get('labels')

            for label in old_labels:
                is_valid_label = True
                if remove_labels is not None:
                    for remove_label in remove_labels:
                        if label.get('name') == remove_label:
                            is_valid_label = False
                if is_valid_label:
                    labels.append(label.get('name'))

            if add_labels is not None:
                for add_label in add_labels:
                    if add_label not in labels:
                        labels.append(add_label)

        data = { 'title': title, 'body': body, 'assignee': assignee, 'state': state, 'milestone': milestone, 'labels': labels }

        util.remove_none(data)

        if data:
            if 'milestone' in data and data['milestone'] == 0:
                data['milestone'] = None

            if is_debug:
                print 'issue_edit, issue %s: %s' % (number, data)
                return data

            url = url = '%s/repos/%s/%s/issues/%s' % (GITHUB_API_URL, repo_username, repo_id, number)
            r = requests.patch(url, data=json.dumps(data), auth=GITHUB_AUTH)

            return r.json()

    except Exception as ex:
        print 'issue_edit, issue %s: %s' % (number, ex)
        return { 'error': '%s' % ex }
