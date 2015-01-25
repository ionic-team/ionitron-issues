# python -m unittest discover

import unittest
from datetime import datetime
from tasks import github_issue_submit as c


class TestGithubIssueSubmit(unittest.TestCase):

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
            'body': '<strong>Type</strong> from submit form',
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
            'body': '<strong>Type</strong>'
        }
        self.assertEquals(c.has_content_from_custom_submit_form(issue), True)
