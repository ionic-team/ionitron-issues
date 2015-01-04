import github3
from config import CONFIG_VARS as cvar


def remove_notice_if_valid(issueNum):
    """
    Removes the notice flag (automated comments and label) if the issue has been
    resubmitted through the custom form on the Ionic site.
    @param issueNum: the issue number that should be refreshed (string)
    @return: whether or not the flag was removed (bool)
    """

    print issueNum
    gh = github3.login(cvar['GITHUB_USERNAME'], cvar['GITHUB_PASSWORD'])
    i = gh.issue(cvar['REPO_USERNAME'], cvar['REPO_ID'], str(issueNum))

    if i.labels:
        labels = [l.name for l in i.labels]
    else:
        labels = []

    if (i.body_html[3:24] == u'<strong>Type</strong>' and cvar['NEEDS_RESUBMIT_LABEL'] in labels):
        i.remove_label(cvar['NEEDS_RESUBMIT_LABEL'])
        comments = list(i.iter_comments())
        [c.delete() for c in comments if c.user.login == cvar['GITHUB_USERNAME']]
        return True

    else:
        return False
