# python -m unittest discover

import unittest
from datetime import datetime
from tasks import github_issue_submit as c
import github_api


class TestGithubIssueSubmit(unittest.TestCase):

    def test_remove_flag_if_submitted_through_github(self):
        issue = {}
        r = c.remove_flag_if_submitted_through_github(issue, is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 123,
            'body': 'blah blah blah i dont get it',
            'labels': []
        }
        r = c.remove_flag_if_submitted_through_github(issue, is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 123,
            'body': '''**Type**: <span ionic-type>docs</span>

                        **Platform**: <span ionic-platform>desktop</span>  <span ionic-webview>browser</span>

                        <span ionic-description>Remove use of :active and instead use classnames</span>

                        <span is-issue-template></span>''',
            'labels': []
        }
        r = c.remove_flag_if_submitted_through_github(issue, is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 123,
            'body': 'blah blah blah i dont get it',
            'labels': [{'name':'ionitron:please resubmit'}]
        }
        r = c.remove_flag_if_submitted_through_github(issue, is_debug=True)
        self.assertEquals(r, False)

        issue = {
            'number': 123,
            'body': '''**Type**: <span ionic-type>docs</span>

                        **Platform**: <span ionic-platform>desktop</span>  <span ionic-webview>browser</span>

                        <span ionic-description>Remove use of :active and instead use classnames</span>

                        <span is-issue-template></span>''',
            'labels': [{'name':'ionitron:please resubmit'}]
        }
        r = c.remove_flag_if_submitted_through_github(issue, is_debug=True)
        self.assertEquals(r, True)


    def test_delete_automated_issue_comments(self):
        comments = [
            { 'id': 1, 'user': { 'login': 'bob' } },
            { 'id': 2, 'user': { 'login': 'bob' } },
            { 'id': 3, 'user': { 'login': 'steve' } },
        ]
        r = github_api.delete_automated_issue_comments(1, comments=comments, is_debug=True, automated_login='steve')
        self.assertEquals(r.get('deleted_automated_issue_comments'), 1)

        comments = [
            { 'id': 1, 'user': { 'login': 'bob' } },
            { 'id': 2, 'user': { 'login': 'steve' } },
            { 'id': 3, 'user': { 'login': 'steve' } },
        ]
        r = github_api.delete_automated_issue_comments(1, comments=comments, is_debug=True, automated_login='steve')
        self.assertEquals(r.get('deleted_automated_issue_comments'), 2)

        comments = [
            { 'user': { 'login': 'bob' } },
            { 'id': 2 },
            { 'id': 3, 'user': { 'login': 'bob' } },
        ]
        r = github_api.delete_automated_issue_comments(1, comments=comments, is_debug=True, automated_login='steve')
        self.assertEquals(r.get('deleted_automated_issue_comments'), 0)

        comments = []
        r = github_api.delete_automated_issue_comments(1, comments=comments, is_debug=True, automated_login='steve')
        self.assertEquals(r.get('deleted_automated_issue_comments'), 0)


    def test_is_valid_issue_opened_source(self):
        needs_resubmit_label = 'ionitron:please resubmit'
        user_orgs = [{
            "login": "driftyco"
        }]

        issue = {
            'body': 'blah blah blah i dont get it',
            'labels': [{'name':'ionitron:please resubmit'}]
        }
        rsp = c.is_valid_issue_opened_source(issue, needs_resubmit_label=needs_resubmit_label, test_is_org_member=False)
        self.assertEquals(rsp, True)

        issue = {
            'body': 'from submit form <span is-issue-template></span>',
        }
        rsp = c.is_valid_issue_opened_source(issue, needs_resubmit_label=needs_resubmit_label, test_is_org_member=False)
        self.assertEquals(rsp, True)

        issue = {
            'body': 'blah blah blah i dont get it',
            'labels': []
        }
        rsp = c.is_valid_issue_opened_source(issue, needs_resubmit_label=needs_resubmit_label, test_is_org_member=False)
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
