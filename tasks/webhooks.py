import github_issue_submit
import maintainence
import models
from main import db


def receive_webhook(event_type, data):
    # add additional event handlers here
    # https://developer.github.com/webhooks/#events
    # https://developer.github.com/v3/activity/events/types/
    try:
        if not event_type or not data:
            return

        action = data.get('action')
        issue = data.get('issue')

        if not issue or not action:
            return

        number = issue.get('number')
        if not number:
            return

        print 'receive_webhook, issue %s, event: %s, action: %s' % (number, event_type, action)

        if event_type == 'issues' and action == 'opened':
            github_issue_submit.flag_if_submitted_through_github(issue)

        elif event_type == 'issues' and action == 'closed':
            existing = models.get_issue(cvar['REPO_USERNAME'], cvar['REPO_ID'], number)
            if existing:
                db.session.delete(existing)
                db.session.commit()
            return

        maintainence.issue_maintainence(issue)

    except Exception as ex:
        print 'receive_webhook, %s, %s: %s' % (event_type, data, ex)


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
