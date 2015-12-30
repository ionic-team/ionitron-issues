import json
from config.config import CONFIG_VARS as cvar
import github_api
import util
import models
from main import db
import issue_score_calculator


def update_issue_score(repo_username, repo_id, number, data={}):
    try:
        if not data.get('issue'):
            data['issue'] = github_api.fetch_issue(repo_username, repo_id, number)
            if not data.get('issue'):
                return

        if not data.get('issue_comments'):
            data['issue_comments'] = github_api.fetch_issue_comments(repo_username, repo_id, number)

        if not data.get('org_members'):
            data['org_members'] = github_api.fetch_org_members_logins(repo_username)

        if not data.get('contributors'):
            data['contributors'] = github_api.fetch_repo_contributors(repo_username, repo_id)

        c = issue_score_calculator.ScoreCalculator(number=number, data=data)
        success = c.load_scores()

        if not success:
            data['load_scores'] = False
            return

        data = c.to_dict()

        cache_key = get_issue_cache_key(repo_username, repo_id, number)
        util.set_cached_data(cache_key, data, 60*60*24*7)

        issue_score = models.IssueScore(repo_username, repo_id, number)
        issue_score.score = data['score']
        issue_score.title = data['title']
        issue_score.comments = data['comments']
        issue_score.references = data['references']
        issue_score.username = data['username']
        issue_score.created = data['created']
        issue_score.updated = data['updated']
        issue_score.avatar = data['avatar']
        issue_score.score_data = json.dumps(data['score_data'])
        issue_score.assignee = data['assignee']
        issue_score.milestone = data['milestone']

        existing = models.get_issue(repo_username, repo_id, number)
        if existing:
            db.session.delete(existing)
            db.session.commit()

        db.session.add(issue_score)
        db.session.commit()

        print 'update_issue_score: %s, score: %s' % (number, data.get('score'))

        return data

    except Exception as ex:
        print 'update_issue_score error, issue %s: %s' % (number, ex)
        return { 'issue_updated': False, 'issue': number, 'error': '%s' % ex }



def get_issue_scores(repo_username, repo_id):
    try:
        data = {
            'repo_username': repo_username,
            'repo_id': repo_id,
            'repo_url': 'https://github.com/%s/%s' % (repo_username, repo_id),
            'repo_issues_url': 'https://github.com/%s/%s/issues' % (repo_username, repo_id),
            'issues': []
        }

        open_issues = github_api.fetch_open_issues(repo_username, repo_id)
        if not open_issues or not isinstance(open_issues, list):
            return { 'error': 'Unable to fetch open issues: %s/%s' % (repo_username, repo_id) }

        for issue in open_issues:
            cache_key = get_issue_cache_key(repo_username, repo_id, issue.get('number'))
            cached_data = util.get_cached_data(cache_key)

            if cached_data:
                milestone = issue.get('milestone')
                if milestone:
                    cached_data['milestone'] = milestone.get('title', '') or ''

                if issue.get('pull_request') is not None:
                    cached_data['pull_request'] = True

                data['issues'].append(cached_data)
                continue

            db_data = models.get_issue(repo_username, repo_id, issue.get('number'))
            if db_data:
                issue_score = db_data.to_dict()

                milestone = issue.get('milestone')
                if milestone:
                    issue_score['milestone'] = milestone.get('title', '') or ''

                if issue.get('pull_request') is not None:
                    issue_score['pull_request'] = True

                data['issues'].append(issue_score)
                continue

            print 'could not find issue calculation: %s' % (cache_key)

        rank_inc = 1
        data['issues'] = sorted(data['issues'], key=lambda k: k['score'], reverse=True)
        for issue in data['issues']:
            issue['rank'] = rank_inc
            issue['repo_username'] = repo_username
            issue['repo_id'] = repo_id
            issue['repo_issue_url'] = 'https://github.com/%s/%s/issues/%s' % (repo_username, repo_id, number),
            rank_inc += 1

        return data

    except Exception as ex:
        print 'get_issue_scores error: %s' % ex
        return { 'error': '%s' % ex }



def get_issue_cache_key(repo_username, repo_id, number):
    return '%s:%s:issue:%s' % (repo_username, repo_id, number)
