import github_issue_submit
import maintainence
import models
import github_api
from main import db


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

        if action == 'updated':
            # not an actual GITHUB action, but faking it from the custom submit form
            # so the issue data it provides is minimal, that's why we're looking it up again
            issue = github_api.fetch_issue(number)
            if not issue or issue.get('error'):
                response['error'] = 'unable to get updated issue'
                response['issue'] = issue
                return response

        response['html_url'] = issue.get('html_url')

        print 'receive_webhook, issue %s, event: %s, action: %s' % (number, event_type, action)

        if event_type == 'issues' and action == 'opened':
            response['flagged_if_submitted_through_github'] = github_issue_submit.flag_if_submitted_through_github(issue)

        elif event_type == 'issues' and action == 'closed':
            existing = models.get_issue(cvar['REPO_USERNAME'], cvar['REPO_ID'], number)
            if existing:
                db.session.delete(existing)
                db.session.commit()
            response['closed'] = True
            return response

        response['issue_maintainence'] = maintainence.issue_maintainence(issue)
        return response

    except Exception as ex:
        print 'receive_webhook, %s, %s: %s' % (event_type, data, ex)
        response['error'] = '%s' % ex

    return response


def test_receive_webhook():
    event_type = 'issues'
    data = {
      "action": "opened",
      "issue": {
        "number": 2,
        "title": "Spelling error in the README file",
        "user": {
          "login": "baxterthehacker"
        },
        "state": "open",
        "assignee": None,
        "milestone": None,
        "comments": 1,
        "created_at": "2016-10-10T00:09:51Z",
        "updated_at": "2016-10-10T00:09:51Z",
        "closed_at": None,
        "body": "<strong>Type</strong>It looks like you accidently spelled 'commit' with two 't's.",
        "labels": [{
            'name': 'ionitron:please resubmit'
        }]
      }
    }
    receive_webhook(event_type, data)
