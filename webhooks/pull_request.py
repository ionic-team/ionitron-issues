import re
import requests
import json
from github3 import pull_request as PullRequest
from config.config import CONFIG_VARS as cvar


def update_commit_status(**kwargs):
    """
    Updates the status of a commit or pull request.
    @kwarg state: can be either pending, success, or failure
    @kwarg context: label to differentiate this status from the status of other systems
    @kwarg description: short description of the status
    @kwarg sha: the commit's sha hash
    @return: a request object containing github's response
    """
    auth = (cvar['GITHUB_USERNAME'], cvar['GITHUB_PASSWORD'])
    url_vars = (cvar['REPO_USERNAME'], cvar['REPO_ID'], kwargs['sha'])
    url = 'https://api.github.com/repos/%s/%s/statuses/%s' % url_vars
    data = {
        'state': kwargs['state'],
        'context': kwargs['context'],
        'description': kwargs['description']
    }
    return requests.post(url, data=json.dumps(data), auth=auth)


def get_feedback_for_msg(commit_msg):
    """
    Generates a list of validation errors for a given message.
    @param commit_msg: a commit message string to validate
    @return: dictionary object:
        'valid': whether or not the message is valid (bool),
        'msg': a list of error messages
    """
    commit_msg = commit_msg.split('\n')[0]
    MAX_LENGTH = 100
    PATTERN = re.compile('^(?:fixup!\s*)?(\w*)(\(([\w\$\.\-\*/]*)\))?\: (.*)$')
    TYPES = [
      'feat',
      'fix',
      'docs',
      'style',
      'refactor',
      'perf',
      'test',
      'chore',
      'revert',
    ]
    feedback = {'valid': False, 'msg': []}
    match = PATTERN.match(commit_msg)

    if match:
        if len(commit_msg) > MAX_LENGTH:
            feedback['msg'].append("- %s is longer than %s characters \n" % (commit_msg, str(MAX_LENGTH)))

        if (match.string != commit_msg):
            feedback['msg'].append("- %s does not match `<type>(<scope>): <subject> \n" % commit_msg)

        if match.group(1) not in TYPES:
            feedback['msg'].append(" - %s is not an allowed type; allowed types are %s" % (match.group(1), str(TYPES)))

    else:
        feedback['msg'].append("- %s does not match `<type>(<scope>): <subject> \n" % commit_msg)

    if not feedback['msg']:
        feedback['valid'] = True

    return feedback


def validate_commit_messages(pr_payload):
    """
    Given a pull_request payload, update the status of the pull request, as
    well as the statuses of individual commits that may have changed.
    @param pr_payload: the payload passed from a pull request cvarent
    @return: dictionary object:
        'pr_title': whether or not pull message is valid (bool),
        'commits': {
                commit_sha: whether or not commit message is valid (bool)
        }
    """
    result = {'pr_title': None, 'commits': {}}
    pr = PullRequest(cvar['REPO_USERNAME'], cvar['REPO_ID'],
                     pr_payload['pull_request']['number'])
    pr_title = pr_payload['pull_request']['title'].split('\n')[0]
    pr_feedback = get_feedback_for_msg(pr_title)

    # Validate the pull request title
    if pr_feedback['valid']:
        update_commit_status(state="success", context="formatting-check",
                             description="commit format is valid",
                             sha=pr_payload['pull_request']['head']['sha'])
        result['pr_title'] = True
    else:
        update_commit_status(state="failure", context="formatting-check",
                             description="\n".join(pr_feedback['msg']),
                             sha=pr_payload['pull_request']['head']['sha'])
        result['pr_title'] = False

    # Validate each individual commit
    commits = list(pr.iter_commits())
    if not commits:
        return result

    for commit in commits:

        sha = pr_payload['pull_request']['head']['sha']
        commit_title = commit.to_json()['commit']['message']
        commit_feedback = get_feedback_for_msg(commit_title)

        if commit_feedback['valid']:
            update_commit_status(state="success", context="formatting-check",
                                 description="commit format is valid",
                                 sha=sha)
            result['commits'][sha] = True
        else:
            update_commit_status(state="failure", context="formatting-check",
                                 description="\n".join(commit_feedback['msg']),
                                 sha=pr_payload['pull_request']['head']['sha'])
            result['commits'][sha] = False

    return result
