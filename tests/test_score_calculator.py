# python -m unittest discover

import unittest
from datetime import datetime
from tasks.issue_score_calculator import ScoreCalculator


class TestScore(unittest.TestCase):

    def test_each_contribution(self):
        scorer = ScoreCalculator(data={
            'contributors': [
                { 'login': 'user1', 'contributions': 10 }
            ],
            'issue': {
                'user': {
                    'login': 'user1'
                }
            }
        })
        scorer.each_contribution(add=2, max_contribution=100)
        self.assertEquals(scorer.score, 20)

        scorer = ScoreCalculator(data={
            'contributors': [
                { 'login': 'user1', 'contributions': 10000 }
            ],
            'issue': {
                'user': {
                    'login': 'user1'
                }
            }
        })
        scorer.each_contribution(add=2, max_contribution=100)
        self.assertEquals(scorer.score, 100)

        scorer = ScoreCalculator(data={
            'contributors': [
                { 'login': 'user2', 'contributions': 10000 }
            ],
            'issue': {
                'user': {
                    'login': 'user1'
                }
            }
        })
        scorer.each_contribution(add=2, max_contribution=100)
        self.assertEquals(scorer.score, 0)

        scorer = ScoreCalculator(data={
            'contributors': [
                { 'login': 'abe', 'contributions': 10000 }
            ],
            'issue': {
                'user': {
                    'login': 'abe'
                }
            },
            'org_members': ['abe', 'jeb', 'rocky']
        })
        scorer.each_contribution(add=2, max_contribution=100)
        self.assertEquals(scorer.score, 0)


    def test_short_title_text(self):
        scorer = ScoreCalculator(data={
            'issue': {
                'title': '123'
            }
        })
        scorer.short_title_text(subtract=50, short_title_text_length=5)
        self.assertEquals(scorer.score, -50)

        scorer = ScoreCalculator(data={
            'issue': {
                'title': '123456'
            }
        })
        scorer.short_title_text(subtract=50, short_title_text_length=5)
        self.assertEquals(scorer.score, 0)


    def test_short_body_text(self):
        scorer = ScoreCalculator(data=setup_data('123'))
        scorer.short_body_text(subtract=50, short_body_text_length=5)
        self.assertEquals(scorer.score, -50)

        scorer = ScoreCalculator(data=setup_data('123456'))
        scorer.short_body_text(subtract=50, short_body_text_length=5)
        self.assertEquals(scorer.score, 0)


    def test_every_x_characters_in_body(self):
        scorer = ScoreCalculator(data=setup_data('1234567890'))
        scorer.every_x_characters_in_body(add=2, x=1)
        self.assertEquals(scorer.score, 20)

        scorer = ScoreCalculator(data=setup_data('1234567890'))
        scorer.every_x_characters_in_body(add=2, x=5)
        self.assertEquals(scorer.score, 4)

        scorer = ScoreCalculator(data=setup_data('1234567890'))
        scorer.every_x_characters_in_body(add=2, x=5, max=3)
        self.assertEquals(scorer.score, 3)

        scorer = ScoreCalculator(data=setup_data(''))
        scorer.every_x_characters_in_body(add=2, x=5)
        self.assertEquals(scorer.score, 0)


    def test_every_x_characters_in_comments(self):
        scorer = ScoreCalculator(data={
            'issue_comments': [
                { 'body': '1234567890', 'user': { 'login': 'rocky' } },
                { 'body': '1234567890', 'user': { 'login': 'steve' } },
                { 'body': '1234567890', 'user': { 'login': 'bill' } },
                { 'body': '1234567890', 'user': { 'login': 'abe' } },
            ],
            'org_members': ['abe', 'jeb', 'rocky']
        })
        scorer.every_x_characters_in_comments(add=3, x=2)
        self.assertEquals(scorer.score, 30)

        scorer = ScoreCalculator(data={
            'issue_comments': [
                { 'body': '1234567890', 'user': { 'login': 'rocky' } },
                { 'body': '1234567890', 'user': { 'login': 'steve' } },
                { 'body': '1234567890', 'user': { 'login': 'bill' } },
                { 'body': '1234567890', 'user': { 'login': 'abe' } },
            ],
            'org_members': ['abe', 'jeb', 'rocky']
        })
        scorer.every_x_characters_in_comments(add=3, x=2, max=15)
        self.assertEquals(scorer.score, 15)

        scorer = ScoreCalculator(data={})
        scorer.every_x_characters_in_comments(add=3, x=2)
        self.assertEquals(scorer.score, 0)


    def test_code_demos(self):
        scorer = ScoreCalculator(data=setup_data('''
            http://codepen.io/agesef HTTPS://jsbin http://plnkr.co HTTP://www.jsfiddle.com/asdfsag/asesd
        '''))
        scorer.code_demos(add=2)
        self.assertEquals(scorer.score, 8)

        scorer = ScoreCalculator(data={
            'issue': {
                'body': 'http://plnkr.co'
            },
            'issue_comments': [
                { 'body': 'http://codepen.io/agesef' },
                { 'body': 'http://codepen.io/agesef' },
                { 'body': 'http://jsbin.io/agesef' },
                { 'body': 'http://jsbin.io/agesef' },
            ]
        })
        scorer.code_demos(add=3)
        self.assertEquals(scorer.score, 9)

        scorer = ScoreCalculator(data={})
        scorer.code_demos(add=2)
        self.assertEquals(scorer.score, 0)


    def test_daily_decay_since_creation(self):
        scorer = ScoreCalculator(data={
            'issue': {
                'created_at': '2000-01-01T00:00:00Z'
            }
        })

        d = scorer.daily_decay_since_creation(exp=1.5, start=50, now=datetime(2000, 1, 11))
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
        scorer = ScoreCalculator(data={
            'issue': {
                'updated_at': '2000-01-01T00:00:00Z'
            }
        })

        d = scorer.daily_decay_since_last_update(exp=1.5, start=50, now=datetime(2000, 1, 11))
        self.assertEquals(d['days_since_update'], 10)
        self.assertEquals(d['start'], 50)
        self.assertEquals(d['score'], 18)

        d = scorer.daily_decay_since_last_update(exp=1.5, start=50, now=datetime(2000, 1, 13))
        self.assertEquals(d['days_since_update'], 12)
        self.assertEquals(d['score'], 8)

        d = scorer.daily_decay_since_last_update(exp=1.5, start=50, now=datetime(2000, 1, 21))
        self.assertEquals(d['days_since_update'], 20)
        self.assertEquals(d['score'], 0.0)


    def test_high_priority(self):
        scorer = ScoreCalculator(data={
            'issue': {
                'labels': [
                  {
                    "name": "bug",
                  }
                ]
            }
        })
        scorer.high_priority(add=2)
        self.assertEquals(scorer.score, 0)

        scorer = ScoreCalculator(data={
            'issue': {
                'labels': [
                  {
                    "name": "high priority",
                  }
                ]
            }
        })
        scorer.high_priority(add=2)
        self.assertEquals(scorer.score, 2)


    def test_awaiting_reply(self):
        scorer = ScoreCalculator(data={
            'issue': {
                'labels': [
                  {
                    "name": "bug",
                  }
                ]
            }
        })
        scorer.awaiting_reply(subtract=2)
        self.assertEquals(scorer.score, 0)

        scorer = ScoreCalculator(data={
            'issue': {
                'labels': [
                  {
                    "name": "needs reply",
                  }
                ]
            }
        })
        scorer.awaiting_reply(subtract=2)
        self.assertEquals(scorer.score, -2)


    def test_each_unique_commenter(self):
        scorer = ScoreCalculator(data={ 'issue_comments': [
            { 'user': { 'login': 'dude1' } },
            { 'user': { 'login': 'dude2' } },
            { 'user': { 'login': 'creator' } },
            { 'user': { 'login': 'creator' } },
            { 'user': { 'login': 'dude3' } },
        ], 'issue': { 'user': { 'login': 'creator' } } })

        scorer.each_unique_commenter(add=2)
        self.assertEquals(scorer.score, 6)

        scorer = ScoreCalculator(data={ 'issue_comments': [
            {'user': { 'login': 'dude1' } },
            {'user': { 'login': 'dude1' } },
            {'user': { 'login': 'dude1' } },
        ] })
        scorer.each_unique_commenter(add=2)
        self.assertEquals(scorer.score, 2)

        scorer = ScoreCalculator(data={ 'issue_comments': [
            { 'user': { 'login': 'dude1' } },
            { 'user': { 'login': 'dude2' } },
            { 'user': { 'login': 'abe' } },
            { 'user': { 'login': 'jeb' } },
            { 'user': { 'login': 'dude2' } },
        ], 'org_members': ['abe', 'jeb', 'rocky'] })
        scorer.each_unique_commenter(add=2)
        self.assertEquals(scorer.score, 4)

        scorer = ScoreCalculator(data={})
        scorer.each_unique_commenter(add=2)
        self.assertEquals(scorer.score, 0)


    def test_each_comment(self):
        scorer = ScoreCalculator(data={ 'issue_comments': [1,2,3] })
        scorer.each_comment(add=2)
        self.assertEquals(scorer.score, 6)

        scorer = ScoreCalculator(data={ 'issue_comments': [1] })
        scorer.each_comment(add=2)
        self.assertEquals(scorer.score, 2)

        scorer = ScoreCalculator(data={})
        scorer.each_comment(add=2)
        self.assertEquals(scorer.score, 0)


    def test_code_snippets(self):
        scorer = ScoreCalculator(data=setup_data('```line1\nline2\nline3```'))
        scorer.code_snippets(add=50, per_line=100, line_max=300)
        self.assertEquals(scorer.score, 350)

        scorer = ScoreCalculator(data=setup_data('whatever text \n```line1\nline2\nline3``` more whatever ```line4```'))
        scorer.code_snippets(add=10, per_line=1)
        self.assertEquals(scorer.score, 14)

        scorer = ScoreCalculator(data=setup_data('Hellow!\n    im code!\n    im code!\n    im code!'))
        scorer.code_snippets(add=10, per_line=1)
        self.assertEquals(scorer.score, 13)

        scorer = ScoreCalculator(data=setup_data('Hellow!\n    im code!\n    im code!\nwhatever```im code!```'))
        scorer.code_snippets(add=10, per_line=1, line_max=2)
        self.assertEquals(scorer.score, 12)

        scorer = ScoreCalculator(data=setup_data('blah blah'))
        scorer.code_snippets(add=2, per_line=1)
        self.assertEquals(scorer.score, 0)

        scorer = ScoreCalculator(data=setup_data('hello\n    me code\n    mecode', issue_comments=[
            { 'body': 'nothing' },
            { 'body': '```code\ncode\ncode```' },
            { 'body': '```code\ncode\ncode``` text ```code\ncode\ncode```' }
        ]))
        scorer.code_snippets(add=10, per_line=1, line_max=100)
        self.assertEquals(scorer.score, 21)


    def test_videos(self):
        scorer = ScoreCalculator(data=setup_data('''
            https://www.dropbox.com/s/gxe6kl1bwzcvcxf/IMG_0229.MOV?dl=0
            https://www.dropbox.com/s/gxe6kl1bwzcvcxf/IMG_0229.MOV?dl=1
            https://www.dropbox.com/s/gxe6kl1bwzcvcxf/IMG_0229.avi?dl=3
        '''))
        scorer.videos(add=2)
        self.assertEquals(scorer.score, 6)

        scorer = ScoreCalculator(data=setup_data('''
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.mp4)
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.qt?asdf)
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.mp4)
        '''))
        scorer.videos(add=2)
        self.assertEquals(scorer.score, 4)

        scorer = ScoreCalculator(data={})
        scorer.videos(add=2)
        self.assertEquals(scorer.score, 0)


    def test_images(self):
        scorer = ScoreCalculator(data=setup_data('''
            <img src="http://hellow.jpg?h=49"> <img src="hi2"> <img src="https://asdf.png">
            <img src="https://asdf.png"> <img src="https://asdf.jpeg">
        '''))
        scorer.images(add=2)
        self.assertEquals(scorer.score, 6)

        scorer = ScoreCalculator(data=setup_data('''
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.gif)
        '''))
        scorer.images(add=2)
        self.assertEquals(scorer.score, 4)

        scorer = ScoreCalculator(data=setup_data('''
            ![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)
        ''', issue_comments=[
            { 'body': 'nothing' },
            { 'body': '<img src="https://asdf.jpeg">' },
            { 'body': '<img src="https://asdf.jpeg">' },
            { 'body': '<img src="https://asdf.gif">' },
            { 'body': '![Image of Yaktocat](https://octodex.github.com/images/yaktocat.png)' }
        ]))
        scorer.images(add=2)
        self.assertEquals(scorer.score, 6)

        scorer = ScoreCalculator(data={})
        scorer.images(add=2)
        self.assertEquals(scorer.score, 0)


    def test_forum_links(self):
        scorer = ScoreCalculator(data=setup_data('''
            http://forum.ionicframework.com http://forum.ionicframework.com
        '''))
        scorer.forum_links(add=2, forum_url='forum.ionicframework.com')
        self.assertEquals(scorer.score, 2)

        scorer = ScoreCalculator(data=setup_data('''
            whatever text
        '''))
        scorer.forum_links(add=2, forum_url='forum.ionicframework.com')
        self.assertEquals(scorer.score, 0)


    def test_links(self):
        scorer = ScoreCalculator(data=setup_data('''
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
        scorer.links(add=2)
        self.assertEquals(scorer.score, 8)

        scorer = ScoreCalculator(data=setup_data('''
            whatever text
        '''))
        scorer.links(add=2)
        self.assertEquals(scorer.score, 0)


    def test_issue_references(self):
        scorer = ScoreCalculator(data=setup_data('''
            I need help yo. Just like issue #123 and issue #456 #456 #456. 10 34534 2323423 5434
        '''))
        scorer.issue_references(add=2)
        self.assertEquals(scorer.score, 4)

        scorer = ScoreCalculator(data=setup_data('''
            This is similar to issue #432 but not #issue.
        ''', issue_comments=[
            { 'body': 'nothing' },
            { 'body': 'Whatever #654 #643 #643 #643' }
        ]))
        scorer.issue_references(add=2)
        self.assertEquals(scorer.score, 6)

        scorer = ScoreCalculator(data=setup_data('''
            2323423
        '''))
        scorer.issue_references(add=2)
        self.assertEquals(scorer.score, 0)




def setup_data(body, login='tester', issue_comments={}, org_members=[]):
    return {
        'issue': {
            'body': body
        },
        'user': {
            'login': login
        },
        'issue_comments': issue_comments,
        'org_members': org_members
    }
