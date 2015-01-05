import unittest
import random
from webhooks.pull_request import get_feedback_for_msg


class TestCommitValidation(unittest.TestCase):

    def test_commit_length_is_excessive(self):
        msg = "docs(foo): " + "".join([random.choice('abcde') for _ in range(100)])
        feedback = get_feedback_for_msg(msg)
        expected = "- %s is longer than %s characters \n" % (msg, '100')
        self.assertEqual(expected, feedback['msg'][0])

    def test_commit_type_is_invalid(self):
        TYPES = [
          'feat',
          'fix',
          'docs',
          'style',
          'refactor',
          'perf',
          'test',
          'chore',
          'revert',
        ]
        msg = "monkey(foo): initial commit"
        feedback = get_feedback_for_msg(msg)
        expected = " - monkey is not an allowed type; allowed types are %s" % str(TYPES)
        self.assertEqual(expected, feedback['msg'][0])

    def test_commit_format_is_invalid(self):
        msg = "who needs commit formatting?"
        feedback = get_feedback_for_msg(msg)
        expected = "- %s does not match `<type>(<scope>): <subject> \n" % msg
        self.assertEqual(expected, feedback['msg'][0])

    def test_commit_format_extracts_title(self):
        msg = "docs(valid): I'm valid \n This is a lot of additional info \
               that isn't in the title, so validation shouldn't be affected."
        feedback = get_feedback_for_msg(msg)
        self.assertEqual(0, len(feedback['msg']))
