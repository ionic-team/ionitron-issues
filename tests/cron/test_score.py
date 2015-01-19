# python -m unittest discover

import random
import unittest
from cron.score import Scorer
from datetime import datetime


class TestScore(unittest.TestCase):

    def test_get_score(self):
        scorer = Scorer(data={})
        scorer.get_score()
        self.assertEquals(scorer.score, 0)


    def test_each_contribution(self):
        scorer = Scorer(data={
            'contributors': [
                { 'login': 'user1', 'contributions': 10 }
            ],
            'user': {
                'login': 'user1'
            }
        })
        scorer.each_contribution(add=2)
        self.assertEquals(scorer.score, 20)

        scorer = Scorer(data={
            'contributors': [
                { 'login': 'user1', 'contributions': 10000 }
            ],
            'user': {
                'login': 'user1'
            }
        })
        scorer.each_contribution(add=2)
        self.assertEquals(scorer.score, 100)

        scorer = Scorer(data={
            'contributors': [
                { 'login': 'user2', 'contributions': 10000 }
            ],
            'user': {
                'login': 'user1'
            }
        })
        scorer.each_contribution(add=2)
        self.assertEquals(scorer.score, 0)


    def test_each_year_since_account_created(self):
        scorer = Scorer(data={
            'user': {
                'created_at': '2000-01-01T00:00:00Z'
            }
        })
        scorer.each_year_since_account_created(add=2, now=datetime(2010, 1, 1))
        self.assertEquals(scorer.score, 20)


    def test_every_x_followers(self):
        scorer = Scorer(data={
            'user': {
                'followers': 100
            }
        })
        scorer.every_x_followers(add=1, x=10)
        self.assertEquals(scorer.score, 10)

        scorer = Scorer(data={
            'user': {}
        })
        scorer.every_x_followers(add=1, x=10)
        self.assertEquals(scorer.score, 0)


    def test_each_public_repo(self):
        scorer = Scorer(data={
            'user': {
                'public_repos': 10
            }
        })
        scorer.each_public_repo(add=1)
        self.assertEquals(scorer.score, 10)

        scorer = Scorer(data={
            'user': {
                'public_repos': 1000
            }
        })
        scorer.each_public_repo(add=1, max_score=50)
        self.assertEquals(scorer.score, 50)

        scorer = Scorer(data={
            'user': {}
        })
        scorer.each_public_repo(add=1)
        self.assertEquals(scorer.score, 0)

        scorer = Scorer(data={})
        scorer.each_public_repo(add=1)
        self.assertEquals(scorer.score, 0)


    def test_each_public_gist(self):
        scorer = Scorer(data={
            'user': {
                'public_gists': 10
            }
        })
        scorer.each_public_gist(add=1)
        self.assertEquals(scorer.score, 10)
        scorer = Scorer(data={
            'user': {
                'public_gists': 1000
            }
        })
        scorer.each_public_gist(add=1, max_score=30)
        self.assertEquals(scorer.score, 30)

        scorer = Scorer(data={})
        scorer.each_public_gist(add=1)
        self.assertEquals(scorer.score, 0)


    def test_has_blog(self):
        scorer = Scorer(data={
            'user': {
                'blog': 'whateves'
            }
        })
        scorer.has_blog(add=1)
        self.assertEquals(scorer.score, 1)

        scorer = Scorer(data={
            'user': {
                'blog': ''
            }
        })
        scorer.has_blog(add=1)
        self.assertEquals(scorer.score, 0)

        scorer = Scorer(data={
            'user': {}
        })
        scorer.has_blog(add=1)
        self.assertEquals(scorer.score, 0)

        scorer = Scorer(data={})
        scorer.has_blog(add=1)
        self.assertEquals(scorer.score, 0)


    def test_every_x_characters_in_body(self):
        scorer = Scorer(data=setup_data('1234567890'))
        scorer.every_x_characters_in_body(add=1, x=1)
        self.assertEquals(scorer.score, 10)

        scorer = Scorer(data=setup_data('1234567890'))
        scorer.every_x_characters_in_body(add=1, x=5)
        self.assertEquals(scorer.score, 2)

        scorer = Scorer(data=setup_data(''))
        scorer.every_x_characters_in_body(add=1, x=5)
        self.assertEquals(scorer.score, 0)


    def test_code_demos(self):
        scorer = Scorer(data=setup_data('''
            codepen jsbin plnkr jsfiddle
        '''))
        scorer.code_demos(add=1)
        self.assertEquals(scorer.score, 4)

        scorer = Scorer(data={})
        scorer.code_demos(add=1)
        self.assertEquals(scorer.score, 0)


    def test_daily_decay_since_creation(self):
        scorer = Scorer(data={
            'issue': {
                'created_at': '2000-01-01T00:00:00Z'
            }
        })

        d = scorer.daily_decay_since_creation(exp=1.5, start=50, now=datetime(2000, 1, 11))
        self.assertEquals(d['created_at_str'], '2000-01-01T00:00:00')
        self.assertEquals(d['days_since_creation'], 10)
        self.assertEquals(d['start'], 50)
        self.assertEquals(d['score'], 18)

        d = scorer.daily_decay_since_creation(exp=1.5, start=50, now=datetime(2000, 1, 13))
        self.assertEquals(d['days_since_creation'], 12)
        self.assertEquals(d['score'], 8)

        d = scorer.daily_decay_since_creation(exp=1.5, start=50, now=datetime(2000, 1, 21))
        self.assertEquals(d['days_since_creation'], 20)
        self.assertEquals(d['score'], 0.0)


    def test_daily_decay_since_last_update(self):
        scorer = Scorer(data={
            'issue': {
                'updated_at': '2000-01-01T00:00:00Z'
            }
        })

        d = scorer.daily_decay_since_last_update(exp=1.5, start=50, now=datetime(2000, 1, 11))
        self.assertEquals(d['updated_at_str'], '2000-01-01T00:00:00')
        self.assertEquals(d['days_since_update'], 10)
        self.assertEquals(d['start'], 50)
        self.assertEquals(d['score'], 18)

        d = scorer.daily_decay_since_last_update(exp=1.5, start=50, now=datetime(2000, 1, 13))
        self.assertEquals(d['days_since_update'], 12)
        self.assertEquals(d['score'], 8)

        d = scorer.daily_decay_since_last_update(exp=1.5, start=50, now=datetime(2000, 1, 21))
        self.assertEquals(d['days_since_update'], 20)
        self.assertEquals(d['score'], 0.0)


    def test_awaiting_reply(self):
        scorer = Scorer(data={
            'issue_labels': [
              {
                "url": "https://api.github.com/repos/octocat/Hello-World/labels/bug",
                "name": "bug",
                "color": "f29513"
              }
            ]
        })
        scorer.awaiting_reply(subtract=1)
        self.assertEquals(scorer.score, 0)

        scorer = Scorer(data={
            'issue_labels': [
              {
                "url": "https://api.github.com/repos/octocat/Hello-World/labels/bug",
                "name": "needs reply",
                "color": "f29513"
              }
            ]
        })
        scorer.awaiting_reply(subtract=1)
        self.assertEquals(scorer.score, -1)


    def test_each_unique_commenter(self):
        scorer = Scorer(data={ 'issue_comments': [
            { 'user': { 'login': 'dude1' } },
            { 'user': { 'login': 'dude2' } },
            { 'user': { 'login': 'dude3' } },
        ] })
        scorer.each_unique_commenter(add=1)
        self.assertEquals(scorer.score, 3)

        scorer = Scorer(data={ 'issue_comments': [
            { 'user': { 'login': 'dude1' } },
            { 'user': { 'login': 'dude1' } },
            { 'user': { 'login': 'dude1' } },
        ] })
        scorer.each_unique_commenter(add=1)
        self.assertEquals(scorer.score, 1)

        scorer = Scorer(data={ 'issue_comments': [
            { 'user': { 'login': 'dude1' } },
            { 'user': { 'login': 'dude2' } },
            { 'user': { 'login': 'abe' } },
            { 'user': { 'login': 'jeb' } },
            { 'user': { 'login': 'dude2' } },
        ], 'team_members': [
            { 'login': 'abe' },
            { 'login': 'jeb' },
            { 'login': 'don' },
        ] })
        scorer.each_unique_commenter(add=1)
        self.assertEquals(scorer.score, 2)

        scorer = Scorer(data={})
        scorer.each_unique_commenter(add=1)
        self.assertEquals(scorer.score, 0)


    def test_each_comment(self):
        scorer = Scorer(data={ 'issue_comments': [1,2,3] })
        scorer.each_comment(add=1)
        self.assertEquals(scorer.score, 3)

        scorer = Scorer(data={ 'issue_comments': [1] })
        scorer.each_comment(add=1)
        self.assertEquals(scorer.score, 1)

        scorer = Scorer(data={})
        scorer.each_comment(add=1)
        self.assertEquals(scorer.score, 0)


    def test_code_snippets(self):
        scorer = Scorer(data=setup_data('```line1\nline2\nline3```'))
        scorer.code_snippets(add=50, per_line=100)
        self.assertEquals(scorer.score, 350)

        scorer = Scorer(data=setup_data('whatever text \n```line1\nline2\nline3``` more whatever ```line4```'))
        scorer.code_snippets(add=10, per_line=1)
        self.assertEquals(scorer.score, 14)

        scorer = Scorer(data=setup_data('Hellow!\n    im code!\n    im code!\n    im code!'))
        scorer.code_snippets(add=10, per_line=1)
        self.assertEquals(scorer.score, 13)

        scorer = Scorer(data=setup_data('Hellow!\n    im code!\n    im code!\nwhatever```im code!```'))
        scorer.code_snippets(add=10, per_line=1, line_max=2)
        self.assertEquals(scorer.score, 12)

        scorer = Scorer(data=setup_data('blah blah'))
        scorer.code_snippets(add=1, per_line=1)
        self.assertEquals(scorer.score, 0)

        scorer = Scorer(data=setup_data('hello\n    me code\n    mecode', issue_comments=[
            { 'body': 'nothing' },
            { 'body': '```code\ncode\ncode```' },
            { 'body': '```code\ncode\ncode``` text ```code\ncode\ncode```' }
        ]))
        scorer.code_snippets(add=10, per_line=1, line_max=100)
        self.assertEquals(scorer.score, 21)


    def test_images(self):
        scorer = Scorer(data=setup_data('''
            <img src="http://hellow.jpg"> <img src="hi2"> <img src="https://asdf.png">
            <img src="https://asdf.png"> <img src="https://asdf.jpeg">
        '''))
        scorer.images(add=1)
        self.assertEquals(scorer.score, 3)

        scorer = Scorer(data=setup_data('''
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.gif)
        '''))
        scorer.images(add=1)
        self.assertEquals(scorer.score, 2)

        scorer = Scorer(data=setup_data('''
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)
        ''', issue_comments=[
            { 'body': 'nothing' },
            { 'body': '<img src="https://asdf.jpeg">' },
            { 'body': '<img src="https://asdf.jpeg">' },
            { 'body': '<img src="https://asdf.gif">' },
            { 'body': '![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)' }
        ]))
        scorer.images(add=1)
        self.assertEquals(scorer.score, 3)

        scorer = Scorer(data={})
        scorer.images(add=1)
        self.assertEquals(scorer.score, 0)


    def test_forum_links(self):
        scorer = Scorer(data=setup_data('''
            http://forum.ionicframework.com http://forum.ionicframework.com
        '''))
        scorer.forum_links(add=1, forum_url='forum.ionicframework.com')
        self.assertEquals(scorer.score, 1)

        scorer = Scorer(data=setup_data('''
            whatever text
        '''))
        scorer.forum_links(add=1, forum_url='forum.ionicframework.com')
        self.assertEquals(scorer.score, 0)


    def test_links(self):
        scorer = Scorer(data=setup_data('''
            http://awesome.com https://awesome.com
            http://image.png http://image.jpeg
        ''', issue_comments=[
            { 'body': 'nothing' },
            { 'body': 'http://asdfasdf' },
            { 'body': 'http://asdfasdf' },
            { 'body': 'https://newlink.com' },
            { 'body': 'https://awesome.com' },
            { 'body': 'https://forum.ionicframework.com/post' },
        ]))
        scorer.links(add=1)
        self.assertEquals(scorer.score, 4)

        scorer = Scorer(data=setup_data('''
            whatever text
        '''))
        scorer.links(add=1)
        self.assertEquals(scorer.score, 0)


    def test_has_issue_reference(self):
        scorer = Scorer(data=setup_data('''
            I need help yo. Just like issue #123 and issue #456. 10 34534 2323423 5434
        '''))
        scorer.has_issue_reference(add=1)
        self.assertEquals(scorer.score, 2)

        scorer = Scorer(data=setup_data('''
            This is similar to issue #432 but not #issue.
        ''', issue_comments=[
            { 'body': 'nothing' },
            { 'body': 'Whatever #654 #643' }
        ]))
        scorer.has_issue_reference(add=1)
        self.assertEquals(scorer.score, 3)

        scorer = Scorer(data=setup_data('''
            2323423
        '''))
        scorer.has_issue_reference(add=1)
        self.assertEquals(scorer.score, 0)




def setup_data(body, login='tester', issue_comments={}, team_members=[]):
    return {
        'issue': {
            'body': body
        },
        'user': {
            'login': login
        },
        'issue_comments': issue_comments,
        'team_members': team_members
    }
