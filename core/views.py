import github3
from config import CONFIG_VARS as cvar
from validator import Issue


def close_old_issues():

    gh = github3.login(cvar['GITHUB_USERNAME'], cvar['GITHUB_PASSWORD'])
    repo = gh.repository(cvar['REPO_USERNAME'], cvar['REPO_ID'])
    issues = repo.iter_issues()

    to_close = [i.number for i in issues if Issue(i).is_valid('close')]

    return {'closed': to_close}


def warn_old_issues():

    gh = github3.login(cvar['GITHUB_USERNAME'], cvar['GITHUB_PASSWORD'])
    repo = gh.repository(cvar['REPO_USERNAME'], cvar['REPO_ID'])
    issues = repo.iter_issues()

    to_warn = [i.number for i in issues if Issue(i).is_valid('warn')]

    return {'warned': to_warn}
