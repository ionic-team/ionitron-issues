
SCORE_VARS = {

    # points to add if submitter is on core team
    'CORE_TEAM': 50,

    # points to add per successful contribution to the repo
    'CONTRIBUTION': 25,
    'CONTRIBUTION_MAX': 100,

    # subtract points when really short title text
    'SHORT_TITLE_TEXT_LENGTH': 25,
    'SHORT_TITLE_TEXT_SUBTRACT': 50,

    # subtract points when really short body text
    'SHORT_BODY_TEXT_LENGTH': 100,
    'SHORT_BODY_TEXT_SUBTRACT': 50,

    # points to ADD for every BODY_CHAR_X characters in issue body
    'BODY_CHAR_ADD': 5,
    'BODY_CHAR_X': 50,

    # points to ADD for every COMMENT_CHAR_X characters in a comment (that is not one of the core team)
    'COMMENT_CHAR_ADD': 1,
    'COMMENT_CHAR_X': 50,

    # points to add for each codepen/plunkr/jsfiddle provided
    'DEMO': 40,
    'DEMO_DOMAINS': ('codepen', 'plnkr', 'jsbin', 'jsfiddle', 'cssdeck', 'dabblet', 'tinkerbin', 'liveweave'),

    # points added to each issue when created or updated
    'CREATED_START': 45,
    'UPDATE_START': 35,

    # this decays quickly, so higher values mean age is more important
    'CREATION_DECAY_EXP': 1.05,
    'LAST_UPDATE_DECAY_EXP': 1.2,

    # subtract if a needs reply label has been applied
    'AWAITING_REPLY': 100,

    # points to add per unique user comment (that is not one of the core team)
    'UNIQUE_USER_COMMENT': 15,

    # points to add for every comment (that is not one of the core team)
    'COMMENT': 2,

    # points to add if issue body contains code snippet
    'SNIPPET': 40,

    # point to add for every line of code
    'SNIPPET_LINE': 2,
    'SNIPPET_LINE_MAX': 50,

    # points to add for every unique image
    'IMAGE': 20,

    # points added for every unique forum link
    'FORUM_LINK': 15,
    'FORUM_URL': 'forum.ionicframework.com',

    # points added for every unqie link thats not a forum or image
    'LINK': 10,

    # points added for other issue references
    'ISSUE_REFERENCE': 10,

}
