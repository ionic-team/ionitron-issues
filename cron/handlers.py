import os
import json
import redis
from cron.score import Scorer
from config.config import CONFIG_VARS as cvar
from cron.network import fetch


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

        open_issue_numbers = [str(oi['number']) for oi in open_issues]

        # only return the cached issues that are open
        cached_issues = db.hmget('issues', open_issue_numbers)

        # cached issues contains a list of json blobs
        result['issues'] = [json.loads(blob) for blob in cached_issues if blob is not None]

    except Exception as ex:
        print 'get_issue_scores error: %s' % ex
        result['error'] = '%s' % ex

    return result


def update_issue_score(iid):
    try:
        redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
        db = redis.from_url(redis_url)

        i = Scorer(iid=iid)
        data = {
            'iid': iid,
            'score': i.get_score(),
            'title': i.data['issue']['title'] or '',
            'number_of_comments': i.number_of_comments,
            'username': i.data['user']['login'] or '',
            'created_at': i.created_at_str or '',
            'updated_at': i.updated_at_str or '',
            'avatar_url': i.data['user']['avatar_url'] or '',
            'score_data': i.score_data
        }
        db.hmset('issues', {iid: json.dumps(data)})

        print 'update_issue_score: %s, score: %s' % (iid, data.get('score'))
        return data

    except Exception, ex:
        print 'update_issue_score error, %s: %s' % (iid, ex)
        return {'issue_updated': False, 'issue': iid}
