# python -m unittest discover

import unittest
from datetime import datetime
from tasks import github_issue_submit as c
import github_api


class TestGithubIssueSubmit(unittest.TestCase):

    def test_remove_flag_if_submitted_through_github(self):
        issue = {}
        r = c.remove_flag_if_submitted_through_github('drifty', 'ionic', issue, is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 123,
            'body': 'blah blah blah i dont get it',
        }
        r = c.remove_flag_if_submitted_through_github('drifty', 'ionic', issue, is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 123,
            'body': '''**Type**: <span ionic-type>docs</span>

                        **Platform**: <span ionic-platform>desktop</span>  <span ionic-webview>browser</span>

                        <span ionic-description>Remove use of :active and instead use classnames</span>

                        <span is-issue-template></span>''',
        }
        r = c.remove_flag_if_submitted_through_github('drifty', 'ionic', issue, issue_comments=[], is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 123,
            'body': 'blah blah blah i dont get it',
        }
        r = c.remove_flag_if_submitted_through_github('drifty', 'ionic', issue, issue_comments=[], is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 123,
            'body': '''**Type**: <span ionic-type>docs</span>

                        **Platform**: <span ionic-platform>desktop</span>  <span ionic-webview>browser</span>

                        <span ionic-description>Remove use of :active and instead use classnames</span>

                        <span is-issue-template></span>''',
        }
        issue_comments = [
            { 'body': '<span ionitron-issue-resubmit></span>' }
        ]
        r = c.remove_flag_if_submitted_through_github('drifty', 'ionic', issue, issue_comments=issue_comments, is_debug=True)
        self.assertEquals(r, True)


    def test_delete_automated_issue_comments(self):
        comments = [
            { 'id': 1, 'user': { 'login': 'bob' } },
            { 'id': 2, 'user': { 'login': 'bob' } },
            { 'id': 3, 'user': { 'login': 'steve' } },
        ]
        r = github_api.delete_automated_issue_comments('drifty', 'ionic', 1, comments=comments, is_debug=True, automated_login='steve')
        self.assertEquals(r.get('deleted_automated_issue_comments'), 1)

        comments = [
            { 'id': 1, 'user': { 'login': 'bob' } },
            { 'id': 2, 'user': { 'login': 'steve' } },
            { 'id': 3, 'user': { 'login': 'steve' } },
        ]
        r = github_api.delete_automated_issue_comments('drifty', 'ionic', 1, comments=comments, is_debug=True, automated_login='steve')
        self.assertEquals(r.get('deleted_automated_issue_comments'), 2)

        comments = [
            { 'user': { 'login': 'bob' } },
            { 'id': 2 },
            { 'id': 3, 'user': { 'login': 'bob' } },
        ]
        r = github_api.delete_automated_issue_comments('drifty', 'ionic', 1, comments=comments, is_debug=True, automated_login='steve')
        self.assertEquals(r.get('deleted_automated_issue_comments'), 0)

        comments = []
        r = github_api.delete_automated_issue_comments('drifty', 'ionic', 1, comments=comments, is_debug=True, automated_login='steve')
        self.assertEquals(r.get('deleted_automated_issue_comments'), 0)


    def test_is_valid_issue_opened_source(self):
        needs_resubmit_content_id = 'ionitron-issue-resubmit'
        user_orgs = [{
            "login": "driftyco"
        }]

        issue = {
            'body': 'blah blah blah i dont get it'
        }
        issue_comments = [
            { 'body': '<span ionitron-issue-resubmit></span>' }
        ]
        rsp = c.is_valid_issue_opened_source('drifty', 'ionic', issue, issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, test_is_org_member=False)
        self.assertEquals(rsp, True)

        issue = {
            'body': 'from submit form <span is-issue-template></span>',
        }
        rsp = c.is_valid_issue_opened_source('drifty', 'ionic', issue, issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, test_is_org_member=False)
        self.assertEquals(rsp, True)

        issue = {
            'body': 'blah blah blah i dont get it',
        }
        rsp = c.is_valid_issue_opened_source('drifty', 'ionic', issue, issue_comments=[], needs_resubmit_content_id=needs_resubmit_content_id, test_is_org_member=False)
        self.assertEquals(rsp, False)


    def test_has_content_from_custom_submit_form(self):
        issue = {
            'body': 'blah blah blah i dont get it'
        }
        self.assertEquals(c.has_content_from_custom_submit_form(issue), False)

        issue = {
            'body': '''**Type**: <span ionic-type>docs</span>

                        **Platform**: <span ionic-platform>desktop</span>  <span ionic-webview>browser</span>

                        <span ionic-description>Remove use of :active and instead use classnames</span>

                        <span is-issue-template></span>'''
        }
        self.assertEquals(c.has_content_from_custom_submit_form(issue), True)


    def test_remove_flag_if_not_updated(self):
        needs_resubmit_content_id = 'ionitron-issue-resubmit'
        now = datetime(2000, 1, 1)

        issue = {
            'number': 1,
            'body': 'blah blah blah i dont get it'
        }
        issue_comments = []
        r = c.remove_flag_if_not_updated('drifty', 'ionic', issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, remove_form_resubmit_comment_after=10, now=now, is_debug=True)
        self.assertEquals(r, False)

        issue = { 'body': '<span ionitron-issue-resubmit></span>' }
        issue_comments = []
        r = c.remove_flag_if_not_updated('drifty', 'ionic', issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, remove_form_resubmit_comment_after=10, now=now, is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 1,
            'body': 'blah blah blah i dont get it'
        }
        issue_comments = [
            { 'body': 'asdf' },
            { 'body': 'asdf' }
        ]
        r = c.remove_flag_if_not_updated('drifty', 'ionic', issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, remove_form_resubmit_comment_after=10, now=now, is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 1,
            'body': 'blah blah blah i dont get it'
        }
        issue_comments = [
            { 'body': '<span ionitron-issue-resubmit></span>' },
            { 'body': 'asdf' }
        ]
        r = c.remove_flag_if_not_updated('drifty', 'ionic', issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, remove_form_resubmit_comment_after=10, now=now, is_debug=True)
        self.assertEquals(r, False)

        now = datetime(2000, 1, 1)
        issue = {
            'number': 1,
            'body': 'blah blah blah i dont get it'
        }
        issue_comments = [
            { 'body': '<span ionitron-issue-resubmit></span>', 'created_at': '2000-01-01T00:00:00Z' },
            { 'body': 'asdf' }
        ]
        r = c.remove_flag_if_not_updated('drifty', 'ionic', issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, remove_form_resubmit_comment_after=10, now=now, is_debug=True)
        self.assertEquals(r, False)

        now = datetime(2000, 1, 12)
        issue = {
            'number': 1,
            'body': 'blah blah blah i dont get it'
        }
        issue_comments = [
            { 'body': '<span ionitron-issue-resubmit></span>', 'created_at': '2000-01-01T00:00:00Z' },
            { 'body': 'asdf' }
        ]
        r = c.remove_flag_if_not_updated('drifty', 'ionic', issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, remove_form_resubmit_comment_after=10, now=now, is_debug=True)
        self.assertEquals(r, True)


    def test_remove_flag_when_closed(self):
        needs_resubmit_content_id = 'ionitron-issue-resubmit'

        issue = {
            'number': 1,
            'body': '<span is-issue-template></span>'
        }
        issue_comments = [
            { 'body': 'asdf', 'id': 1 }
        ]
        r = c.remove_flag_when_closed('drifty', 'ionic', issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 1,
            'body': '<span is-issue-template></span>'
        }
        issue_comments = [
            { 'body': 'asdf', 'id': 1 },
            { 'body': '<span ionitron-issue-resubmit></span>', 'id':2 },
        ]
        r = c.remove_flag_when_closed('drifty', 'ionic', issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, is_debug=True)
        self.assertEquals(r, False)

        needs_resubmit_content_id = 'ionitron-issue-resubmit'

        issue = {
            'number': 1,
            'body': 'blah blah blah i dont get it'
        }
        issue_comments = [
            { 'body': 'asdf', 'id': 1 }
        ]
        r = c.remove_flag_when_closed('drifty', 'ionic', issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 1,
            'body': 'blah blah blah i dont get it'
        }
        issue_comments = [
            { 'body': '<span ionitron-issue-resubmit></span>', 'id': 1 },
            { 'body': 'asdf', 'id': 2 }
        ]
        r = c.remove_flag_when_closed('drifty', 'ionic', issue, issue_comments=issue_comments, needs_resubmit_content_id=needs_resubmit_content_id, is_debug=True)
        self.assertEquals(r, True)


    def test_add_docs_label(self):
        issue = {
            'number': 1,
            'title': 'some issue title',
            'body': '**Ionic Version**: 1.x'
        }
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(r[0], 'v1')

        issue = {
            'number': 1,
            'title': 'some issue title',
            'body': 'issue body'
        }
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(len(r), 0)

        issue['title'] = 'docs(): some issue title'
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(r[0], 'docs')

        issue['title'] = 'DOCS: some issue title'
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(r[0], 'docs')

        issue['title'] = 'DoCs) some issue title'
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(r[0], 'docs')

        issue['title'] = 'docs some issue title'
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(r[0], 'docs')

        issue['title'] = 'docs some issue title'
        issue['labels'] = [{'name': 'docs'}]
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(len(r), 0)


    def test_add_v2_label(self):
        issue = {
            'number': 1,
            'title': 'some issue title',
            'body': 'issue body'
        }
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(len(r), 0)

        issue = {
            'number': 1,
            'title': 'V2: some issue title',
            'body': 'issue body'
        }
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(r[0], 'v2')

        issue = {
            'number': 1,
            'title': 'bug@v2: some issue title',
            'body': 'issue body'
        }
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(r[0], 'v2')

        issue = {
            'number': 1,
            'title': 'some issue title',
            'body': '**Ionic Version**: 2.x'
        }
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(r[0], 'v2')

        issue['body'] = 'some issue title <span ionic-version>2.x</span>'
        r = c.add_label_from_content('drifty', 'ionic', issue)
        self.assertEquals(r[0], 'v2')
