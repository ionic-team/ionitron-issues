import os
import json
import redis
from cron.score import Scorer
from config.config import CONFIG_VARS as cvar
from cron.network import fetch
import time


def get_issue_scores():
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
            issue_data = db.get(db_key)
            if issue_data:
                result['issues'].append(json.loads(issue_data))
            else:
                print 'could not find issue calculation: %s' % (db_key)

    except Exception as ex:
        print 'get_issue_scores error: %s' % ex
        result['error'] = '%s' % ex

    return result


def update_issue_score(iid, throttle_recalculation=False):
    try:
        redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
        db = redis.from_url(redis_url)

        db_key = get_issue_db_key(iid)

        if throttle_recalculation:
            try:
                db_data = db.get(db_key)
                if db_data:
                    cached_data = json.loads(db_data)
                    calculated = cached_data.get('calculated')
                    if calculated and calculated + 21600000 > int(time.time()) * 1000:
                        print 'recently calculated: %s' % cached_data.get('calculated')
                        return { 'issue_updated': False, 'issue': iid, 'calculated': '%s' % calculated }

            except Exception as cacheEx:
                print 'update_issue_score cache lookup error, %s: %s' % (db_key, cacheEx)

        i = Scorer(iid=iid)
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
            'calculated': int(time.time()) * 1000
        }

        db.setex(db_key, json.dumps(data), 60*60*24*7)

        print 'update_issue_score: %s, score: %s' % (db_key, data.get('score'))
        return data

    except Exception as ex:
        print 'update_issue_score error, %s: %s' % (iid, ex)
        return { 'issue_updated': False, 'issue': iid, 'error': '%s' % ex }


def get_issue_db_key(iid):
    return '%s:%s:issue:%s' % (cvar['REPO_USERNAME'], cvar['REPO_ID'], iid)
