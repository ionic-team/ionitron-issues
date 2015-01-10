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
    result = []

    try:
        open_issues = fetch('issues', '/repos/%s/%s/issues?' % (rname, rid))['issues']
        open_issue_numbers = [str(oi['number']) for oi in open_issues]
        # only return the cached issues that are open
        cached_issues = db.hmget('issues', open_issue_numbers)
        # cached issues contains a list of json blobs
        result = [json.loads(blob) for blob in cached_issues if blob is not None]
    except Exception, e:
        print "Cannot fetch open issues. This may mean the Github " +\
              "account being used in being throttled."
        print e
        result = []

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
        }
        db.hmset('issues', {iid: json.dumps(data)})
        return {'issue_updated': True}

    except Exception, e:
        print e
        return {'issue_updated': False}
