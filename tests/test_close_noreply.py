# python -m unittest discover

import unittest
from datetime import datetime
from tasks import needs_reply as c


class TestCloseNoReply(unittest.TestCase):

    def test_has_needs_reply_label(self):
        self.assertEquals(c.has_needs_reply_label(None), False)
        self.assertEquals(c.has_needs_reply_label({}), False)

        self.assertEquals(c.has_needs_reply_label({
            'labels': None
        }), False)

        self.assertEquals(c.has_needs_reply_label({
            'labels': []
        }), False)

        self.assertEquals(c.has_needs_reply_label({
            'labels': [{
                'name': 'bug'
            }]
        }), False)

        self.assertEquals(c.has_needs_reply_label({
            'labels': [{
                'name': 'needs reply'
            }]
        }), True)


    def test_get_most_recent_datetime_need_reply_label_added(self):
        self.assertEquals(c.get_most_recent_datetime_need_reply_label_added(None), None)

        self.assertEquals(c.get_most_recent_datetime_need_reply_label_added([]), None)

        self.assertEquals(c.get_most_recent_datetime_need_reply_label_added([{
            'event': 'closed'
        }]), None)

        self.assertEquals(c.get_most_recent_datetime_need_reply_label_added([{
            'event': 'labeled'
        }]), None)

        self.assertEquals(c.get_most_recent_datetime_need_reply_label_added([{
            'event': 'labeled',
            'label': None
        }]), None)

        self.assertEquals(c.get_most_recent_datetime_need_reply_label_added([{
            'event': 'labeled',
            'label': []
        }]), None)

        self.assertEquals(c.get_most_recent_datetime_need_reply_label_added([{
            'event': 'labeled',
            'label': {
                'name': 'bug'
            }
        }]), None)

        self.assertEquals(c.get_most_recent_datetime_need_reply_label_added([{
            'event': 'labeled',
            'label': {
                'name': 'needs reply'
            }
        }]), None)

        self.assertEquals(c.get_most_recent_datetime_need_reply_label_added([{
            'event': 'labeled',
            'label': {
                'name': 'needs reply'
            },
            'created_at': '2000-01-02T00:00:00Z'
        }]), datetime(2000, 1, 2, 0, 0))

        self.assertEquals(c.get_most_recent_datetime_need_reply_label_added([{
            'event': 'labeled',
            'label': {
                'name': 'needs reply'
            },
            'created_at': '2000-01-02T00:00:00Z'
        },{
            'event': 'labeled',
            'label': {
                'name': 'needs reply'
            },
            'created_at': '2000-01-05T00:00:00Z'
        },{
            'event': 'labeled',
            'label': {
                'name': 'needs reply'
            },
            'created_at': '2000-01-03T00:00:00Z'
        },{
            'event': 'labeled',
            'label': {
                'name': 'bug'
            },
            'created_at': '2000-01-10T00:00:00Z'
        }]), datetime(2000, 1, 5, 0, 0))


    def test_get_most_recent_datetime_creator_response(self):
        self.assertEquals(
            c.get_most_recent_datetime_creator_response(None, None),
            None)

        self.assertEquals(
            c.get_most_recent_datetime_creator_response({
                'user': None
            }, None),
            None)

        self.assertEquals(
            c.get_most_recent_datetime_creator_response({
                'user': { 'login': None }
            }, None),
            None)

        self.assertEquals(
            c.get_most_recent_datetime_creator_response({
                'user': { 'login': 'steve' }
            }, None),
            None)

        self.assertEquals(
            c.get_most_recent_datetime_creator_response({
                'user': { 'login': 'steve' },
                'created_at': '2000-01-01T00:00:00Z'
            }, None),
            datetime(2000, 1, 1, 0, 0))

        self.assertEquals(
            c.get_most_recent_datetime_creator_response({
                'user': { 'login': 'steve' },
                'created_at': '2000-01-01T00:00:00Z'
            }, []),
            datetime(2000, 1, 1, 0, 0))

        self.assertEquals(
            c.get_most_recent_datetime_creator_response({
                'user': { 'login': 'steve' },
                'created_at': '2000-01-01T00:00:00Z'
            }, [
                { 'user': { 'login': 'bob' }, 'created_at': '2000-02-01T00:00:00Z' },
                { 'user': { 'login': 'steve' }, 'created_at': '2000-03-01T00:00:00Z' },
                { 'user': { 'login': 'don' }, 'created_at': '2000-04-01T00:00:00Z' },
            ]),
            datetime(2000, 3, 1, 0, 0))


    def test_has_replied_since_adding_label(self):
        self.assertEquals(
            c.has_replied_since_adding_label(datetime(2000, 1, 1), datetime(2000, 2, 1)), True)

        self.assertEquals(
            c.has_replied_since_adding_label(datetime(2000, 2, 1), datetime(2000, 1, 1)), False)


    def test_has_not_replied_in_timely_manner(self):
        self.assertEquals(
            c.has_replied_in_timely_manner(datetime(2000, 1, 1), datetime(2000, 2, 1), 10),
            False)

        self.assertEquals(
            c.has_replied_in_timely_manner(datetime(2000, 1, 1), datetime(2000, 1, 2), 10),
            True)

        self.assertEquals(
            c.has_replied_in_timely_manner(datetime(2000, 1, 1), datetime(2000, 1, 9), 10),
            True)

        self.assertEquals(
            c.has_replied_in_timely_manner(datetime(2000, 1, 1), datetime(2001, 1, 11), 10),
            False)


    def test_remove_needs_reply_comment(self):
        needs_reply_content_id = 'ionitron-needs-reply'

        issue = {
            'number': 1,
            'body': 'blah blah blah i dont get it'
        }
        issue_comments = [
            { 'body': 'asdf', 'id': 1 }
        ]
        r = c.remove_needs_reply_comment(issue, issue_comments=issue_comments, needs_reply_content_id=needs_reply_content_id, is_debug=True)
        self.assertEquals(r, 'no comment to remove')


        issue = {
            'number': 1,
            'body': 'blah blah blah i dont get it'
        }
        issue_comments = [
            { 'body': 'ionitron-needs-reply', 'id': 1 }
        ]
        r = c.remove_needs_reply_comment(issue, issue_comments=issue_comments, needs_reply_content_id=needs_reply_content_id, is_debug=True)
        self.assertEquals(r, 'removed auto comment')


