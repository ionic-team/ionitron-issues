
SCORE_VARS = {

    # points to add if submitter is on core team
    'CORE_TEAM': 50,

    # points to add per successful contribution
    'CONTRIBUTION': 30,

    # points to remove for a new account
    'NEW_ACCOUNT': 15,

    # points to add for every year since github account created
    'GITHUB_YEARS': 3,

    # points to ADD for every FOLLOWERS_X followers
    'FOLLOWERS_ADD': 1,
    'FOLLOWERS_X': 5,

    # points to add per public repo
    'PUBLIC_REPOS': 3,

    # points to add per public gist
    'PUBLIC_GISTS': 1,

    # points to remove per issue submitted that bot removed
    'BOT_CLOSED': 20,

    # points to add if user has blog
    'BLOG': 7,

    # points to add if issue has image
    'IMAGE': 20,

    # points to ADD for every CHAR_X characters in issue body
    'CHAR_ADD': 5,
    'CHAR_X': 100,

    # points to add for each codepen/plunkr/jsfiddle provided
    'DEMO': 40,
    'DEMO_DOMAINS': ('codepen', 'jsbin', 'jsfiddle', 'cssdeck', 'dabblet', 'tinkerbin', 'liveweave', 'plnkr'),

    # points added to each issue when created or updated
    'CREATED_START': 45,
    'UPDATE_START': 35,

    # this decays quickly, so higher values mean age is more important
    'CREATION_DECAY_EXP': 1.05,
    'LAST_UPDATE_DECAY_EXP': 1.2,

    # subtract if a needs reply label has been applied
    'AWAITING_REPLY': 100,

    # points to add per comment
    'COMMENT': 15,

    # points to add if issue body contains code snippet
    'SNIPPET': 40,
    'SNIPPET_LINE': 2,
    'SNIPPET_LINE_MAX': 50,

    # points added when issue body contains a regex match of FORUM_URL
    'FORUM_ADD': 20,
    'FORUM_URL': 'forum.ionicframework.com',

    # points added for every link
    'LINK': 5,

    # points added for other issue references
    'ISSUE_REFERENCE': 10,

}
