import os
import json
import redis
from cron.score import Scorer
from config.config import CONFIG_VARS as cvar
from cron.network import fetch
import time


def get_issue_scores():
    import models
    from main import db
    """
    Gets the scores calculated for all currently open issues.
    @return: list containing a dictionary for each issue, each
             dictionary has contains issue score, and a number
             of other attributes. See cron.handler.update_issue_score
             for a full list of attributes.
    """
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    db = redis.from_url(redis_url)
    rname = cvar['REPO_USERNAME']
    rid = cvar['REPO_ID']
    result = {
        'org': rname,
        'repo': rid,
        'repo_url': 'https://github.com/%s/%s' % (rname, rid),
        'issues': []
    }

    try:
        data = fetch('issues', '/repos/%s/%s/issues?' % (rname, rid))

        open_issues = data.get('issues')
        if data.get('error') or not open_issues:
            return data

        open_issue_numbers = [oi['number'] for oi in open_issues]

        for iid in open_issue_numbers:
            db_key = get_issue_db_key(int(iid))
            cached_data = db.get(db_key)
            if cached_data:
                result['issues'].append(json.loads(cached_data))
                continue

            db_data = models.get_issue(cvar['REPO_USERNAME'], cvar['REPO_ID'], iid)
            if db_data:
                result['issues'].append(db_data.to_dict())
                continue

            print 'could not find issue calculation: %s' % (db_key)

        index_inc = 0
        result['issues'] = sorted(result['issues'], key=lambda k: k['score'], reverse=True)
        for issue in result['issues']:
            issue['index'] = index_inc
            index_inc += 1

    except Exception as ex:
        print 'get_issue_scores error: %s' % ex
        result['error'] = '%s' % ex

    return result


def update_issue_score(iid, issue_data=None, throttle_recalculation=False):
    try:
        redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
        db = redis.from_url(redis_url)

        db_key = get_issue_db_key(iid)

        if throttle_recalculation and False:
            try:
                db_data = db.get(db_key)
                if db_data:
                    cached_data = json.loads(db_data)
                    calculated = cached_data.get('calculated')
                    if calculated and calculated + 43200000 > int(time.time()) * 1000:
                        print 'recently calculated: %s' % cached_data.get('calculated')
                        return { 'issue_updated': False, 'issue': iid, 'calculated': '%s' % calculated }

            except Exception as cacheEx:
                print 'update_issue_score cache lookup error, %s: %s' % (db_key, cacheEx)

        i = Scorer(iid=iid, data=issue_data)

        assignee = ''
        if i.data.get('assignee'):
            assignee = i.data['assignee'].get('login')

        data = {
            'iid': iid,
            'score': i.get_score(),
            'title': i.data['issue']['title'] or '',
            'comments': i.number_of_comments,
            'username': i.data['user']['login'] or '',
            'created': i.created_at_str or '',
            'updated': i.updated_at_str or '',
            'avatar': i.data['user']['avatar_url'] or '',
            'score_data': i.score_data,
            'assignee': assignee,
            'calculated': int(time.time()) * 1000
        }

        db.setex(db_key, json.dumps(data), 60*60*24*7)

        import models
        from main import db

        issue_score = models.IssueScore(cvar['REPO_USERNAME'], cvar['REPO_ID'], iid)
        issue_score.score = data['score']
        issue_score.title = data['title']
        issue_score.comments = data['comments']
        issue_score.username = data['username']
        issue_score.created = data['created']
        issue_score.updated = data['updated']
        issue_score.avatar = data['avatar']
        issue_score.score_data = json.dumps(data['score_data'])
        issue_score.assignee = data['assignee']

        existing = models.get_issue(cvar['REPO_USERNAME'], cvar['REPO_ID'], iid)
        if existing:
            db.session.delete(existing)
            db.session.commit()

        db.session.add(issue_score)
        db.session.commit()

        print 'update_issue_score: %s, score: %s' % (db_key, data.get('score'))
        return data

    except Exception as ex:
        print 'update_issue_score error, %s: %s' % (iid, ex)
        return { 'issue_updated': False, 'issue': iid, 'error': '%s' % ex }


def get_issue_db_key(iid):
    return '%s:%s:issue:%s' % (cvar['REPO_USERNAME'], cvar['REPO_ID'], iid)
