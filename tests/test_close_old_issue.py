# python -m unittest discover

import unittest
from datetime import datetime
from tasks import old_issues as c


class TestCloseOldIssue(unittest.TestCase):

    def test_is_closed_issue(self):
        self.assertEquals(c.is_closed({'closed_at': None}), False)
        self.assertEquals(c.is_closed({'closed_at': "2014-10-10T00:09:51Z"}), True)

    def test_is_pull_request(self):
        self.assertEquals(c.is_pull_request({}), False)
        self.assertEquals(c.is_pull_request({'pull_request': {}}), True)

    def test_has_milestone(self):
        self.assertEquals(c.has_milestone({'milestone': None}), False)
        self.assertEquals(c.has_milestone({'milestone': "v1.1"}), True)

    def test_is_old_issue(self):
        self.assertEquals(c.is_old_issue(datetime(2000, 1, 1), now=datetime(2000, 1, 9), close_inactive_after=10), False)
        self.assertEquals(c.is_old_issue(datetime(2000, 1, 1), now=datetime(2000, 1, 11), close_inactive_after=10), False)
        self.assertEquals(c.is_old_issue(datetime(2000, 1, 1), now=datetime(2000, 1, 12), close_inactive_after=10), True)

    def test_has_labels_preventing_close(self):
        self.assertEquals(c.has_labels_preventing_close({
            'labels': [{
                'name': 'bug'
            }]
        }, ['in progress', 'ready', 'high priority']), False)

        self.assertEquals(c.has_labels_preventing_close({}, ['in progress', 'ready', 'high priority']), False)

        self.assertEquals(c.has_labels_preventing_close({ 'labels': [] }, ['in progress', 'ready', 'high priority']), False)

        self.assertEquals(c.has_labels_preventing_close({
            'labels': [{
                'name': 'ready'
            }]
        }, ['in progress', 'ready', 'high priority']), True)

    def test_has_comments_preventing_close(self):
        self.assertEquals(c.has_comments_preventing_close({
            'comments': None
        }, 2), False)

        self.assertEquals(c.has_comments_preventing_close({
            'comments': 0
        }, 2), False)

        self.assertEquals(c.has_comments_preventing_close({
            'comments': 2
        }, 2), False)

        self.assertEquals(c.has_comments_preventing_close({
            'comments': 3
        }, 2), True)

    def test_has_assignee_preventing_close(self):
        self.assertEquals(c.has_assignee_preventing_close({
            'assignee': None
        }), False)

        self.assertEquals(c.has_assignee_preventing_close({
            'assignee': {}
        }), False)

        self.assertEquals(c.has_assignee_preventing_close({
            'assignee': { 'login': 'steve' }
        }), True)

    def test_has_milestone_preventing_close(self):
        self.assertEquals(c.has_milestone_preventing_close({}), False)

        self.assertEquals(c.has_milestone_preventing_close({
            'milestone': None
        }), False)

        self.assertEquals(c.has_milestone_preventing_close({
            'milestone': {}
        }), False)

        self.assertEquals(c.has_milestone_preventing_close({
            'milestone': { 'url': 'https://api.github.com/repos/octocat/Hello-World/milestones/1' }
        }), True)


    def test_has_events_preventing_close(self):
        self.assertEquals(c.has_events_preventing_close(None), False)

        self.assertEquals(c.has_events_preventing_close([
            { 'event': 'closed' },
            { 'event': 'labeled' }
        ]), False)

        self.assertEquals(c.has_events_preventing_close([
            { 'event': 'closed' },
            { 'event': 'referenced' }
        ]), True)
