import os
import json
import redis
from config.config import CONFIG_VARS as cvar
from cron.network import fetch


def get_issue_scores():
    """
    Gets the scores calculated for all currently open issues.
    @return: {iid: score}
    """
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    db = redis.from_url(redis_url)
    rname = cvar['REPO_USERNAME']
    rid = cvar['REPO_ID']

    cached_issues = db.hgetall('issues')
    # open_issues = fetch('issues', '/repos/%s/%s/issues?' % (rname, rid))

    # only return the scores of issues that are open
    # return [cached_issues[i['number']] for i in open_issues]

    # data is stored in mapping of iid to json blob, convert
    result = [json.loads(v) for v in cached_issues.values()]

    return result
