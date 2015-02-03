
SCORE_VARS = {

    # points to add if submitter is on core team
    'CORE_TEAM': 100,

    # points to add per successful contribution to the repo
    'CONTRIBUTION': 50,
    'CONTRIBUTION_MAX': 400,

    # subtract points when really short title text
    'SHORT_TITLE_TEXT_LENGTH': 25,
    'SHORT_TITLE_TEXT_SUBTRACT': 50,

    # subtract points when really short body text
    'SHORT_BODY_TEXT_LENGTH': 100,
    'SHORT_BODY_TEXT_SUBTRACT': 50,

    # points to ADD for every BODY_CHAR_X characters in issue body
    'BODY_CHAR_ADD': 10,
    'BODY_CHAR_X': 50,
    'BODY_CHAR_MAX': 250,

    # points to ADD for every COMMENT_CHAR_X characters in a comment (that is not one of the core team)
    'COMMENT_CHAR_ADD': 5,
    'COMMENT_CHAR_X': 50,
    'COMMENT_CHAR_MAX': 200,

    # points added to each issue when created or updated
    'CREATED_START': 45,
    'UPDATE_START': 35,

    # this decays quickly, so higher values mean age is more important
    'CREATION_DECAY_EXP': 1.1,
    'LAST_UPDATE_DECAY_EXP': 1.2,

    # points to ADD for having a high priority label
    'HIGH_PRIORITY': 200,

    # subtract if a needs reply label has been applied
    'AWAITING_REPLY': 100,

    # points to add per unique user comment (that is not one of the core team or the issue creator)
    'UNIQUE_USER_COMMENT': 20,

    # points to add for every comment (that is not one of the core team)
    'COMMENT': 2,

    # points to add if issue body contains code snippet
    'SNIPPET': 50,

    # point to add for every line of code
    'SNIPPET_LINE': 5,
    'SNIPPET_LINE_MAX': 200,

    # points to add for each codepen/plunkr/jsfiddle provided
    'DEMO': 50,
    'DEMO_DOMAINS': ('codepen', 'plnkr', 'jsbin', 'jsfiddle', 'cssdeck', 'dabblet', 'tinkerbin', 'liveweave'),

    # points to add for every unique video
    'VIDEO': 35,

    # points to add for every unique image
    'IMAGE': 25,

    # points added for every unique forum link
    'FORUM_LINK': 20,
    'FORUM_URL': 'forum.ionicframework.com',

    # points added for every unqie link thats not a forum or image
    'LINK': 10,

    # points added for other issue references
    'ISSUE_REFERENCE': 20,

}
