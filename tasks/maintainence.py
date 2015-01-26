import threading
import util
import datetime
from worker import q
import github_api


def queue_daily_tasks():
    cache_db = util.get_cache_db()

    # Do not update if scores have been updated within past 24 hours
    last_update = cache_db.get('last_update')
    print 'Queueing daily tasks, last update: %s' % last_update

    if last_update:
        then = datetime.datetime.fromordinal(int(last_update))
        now = datetime.datetime.now()
        if (now - then).seconds >= 600:
            q.enqueue(run_maintainence_tasks)
            cache_db.set('last_update', now.toordinal())
    else:  # last update time hasn't been set. Set it so it runs in 24 hours
        cache_db.set('last_update', datetime.datetime.now().toordinal())

    # Rerun daily tasks in 24 hours
    threading.Timer(60*60*24, queue_daily_tasks).start()


def run_maintainence_tasks():
    """
    Maintainence tasks to run on older issues.
    """
    print "Running daily tasks..."

    open_issues = []
    try:
        open_issues = github_api.fetch_open_issues()
        if not open_issues:
            return open_issues

        for issue in open_issues:
            issue_maintainence(issue)

    except Exception as ex:
        print 'run_maintainence_tasks error: %s' % ex

    return len(open_issues)


def issue_maintainence_number(number):
    try:
        issue = github_api.fetch_issue(number)

        if issue.get('error'):
            return issue

        return issue_maintainence(issue)

    except Exception as ex:
        print 'run_maintainence_tasks error: %s' % ex
        return { 'error': '%s' % ex }


def issue_maintainence(issue):
    from tasks import old_issues, github_issue_submit, needs_reply, issue_scores
    data = {}
    number = 0

    try:
        if not issue:
            data['error'] = 'invalid issue'
            return data

        number = issue.get('number')
        if not number:
            data['error'] = 'invalid issue number'
            return data

        data['number'] = number

        if issue.get('pull_request') is not None:
            data['invalid'] = 'pull request'
            return data

        if issue.get('closed_at') is not None:
            data['invalid'] = 'closed_at %s' % issue.get('closed_at')
            return data

        old_issue_data = old_issues.manage_old_issue(issue)
        if old_issue_data:
            data['closed_old_issue'] = True
            return data

        if github_issue_submit.remove_flag_if_submitted_through_github(issue):
            data['removed_submitted_through_github_flag'] = True

        needs_reply_data = needs_reply.manage_needs_reply_issue(issue)
        if needs_reply_data:
            data['needs_reply_data'] = needs_reply_data
            if needs_reply_data.get('close_needs_reply_issue'):
                return data

        data['issue_score'] = issue_scores.update_issue_score(number, data={
            'issue': issue
        })

    except Exception as ex:
        print 'issue_maintainence error, issue %s: %s' % (number, ex)
        data['error'] = 'issue %s, %s' % (number, ex)

    return data
