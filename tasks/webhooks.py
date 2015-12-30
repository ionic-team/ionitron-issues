import github_issue_submit
import maintainence
import models
import github_api
from main import db
from config.config import CONFIG_VARS as cvar


def receive_webhook(event_type, data):
    # add additional event handlers here
    # https://developer.github.com/webhooks/#events
    # https://developer.github.com/v3/activity/events/types/
    response = {
        'event_type': event_type
    }
    try:
        if not event_type:
            print 'receive_webhook, missing event_type'
            response['error'] = 'missing event_type'
            return response

        if not data:
            print 'receive_webhook, missing data'
            response['error'] = 'missing data'
            return response

        action = data.get('action')

        if not action:
            print 'receive_webhook, missing action'
            response['error'] = 'missing action'
            return response

        response['action'] = action

        issue = data.get('issue')
        if not issue:
            print 'receive_webhook, missing issue'
            response['error'] = 'missing issue'
            return response

        number = issue.get('number')
        if not number:
            print 'receive_webhook, missing issue number'
            response['error'] = 'missing issue number'
            return response

        response['number'] = number

        repository = data.get('repository')
        if not repository:
            print 'receive_webhook, missing repository'
            response['error'] = 'missing repository'
            return response

        repo_id = repository.get('name')

        repository_owner = repository.get('owner')
        if not repository_owner:
            print 'receive_webhook, missing repository_owner'
            response['error'] = 'missing repository_owner'
            return response

        repo_username = repository_owner.get('login')

        if action == 'updated':
            # not an actual GITHUB action, but faking it from the custom submit form
            # so the issue data it provides is minimal, that's why we're looking it up again
            issue = github_api.fetch_issue(repo_username, repo_id, number)
            if not issue or issue.get('error'):
                response['error'] = 'unable to get updated issue'
                response['issue'] = issue
                return response

        response['html_url'] = issue.get('html_url')

        print 'receive_webhook, %s %s, issue %s, event: %s, action: %s' % (repo_username, repo_id, number, event_type, action)

        if event_type == 'issues' and action == 'opened':
            response['flagged_if_submitted_through_github'] = github_issue_submit.flag_if_submitted_through_github(repo_username, repo_id, issue)

        elif event_type == 'issues' and action == 'closed':
            existing = models.get_issue(repo_username, repo_id, number)
            if existing:
                db.session.delete(existing)
                db.session.commit()
            github_issue_submit.remove_flag_when_closed(repo_username, repo_id, issue)
            response['closed'] = True
            return response

        response['issue_maintainence'] = maintainence.issue_maintainence(repo_username, repo_id, issue)
        return response

    except Exception as ex:
        print 'receive_webhook, %s, %s: %s' % (event_type, data, ex)
        response['error'] = '%s' % ex

    return response
