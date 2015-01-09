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
        print result
        result = []

    return result
