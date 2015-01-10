
SCORE_VARS = {

    # points to add if submitter is on core team
    'CORE_TEAM': 80,
    # points to add per successful contribution
    'CONTRIBUTION': 20,
    # points to remove for a new account
    'NEW_ACCOUNT': 15,
    # points to add for every year since github account created
    'GITHUB_YEARS': 6,
    # points to add per public repo
    'PUBLIC_REPOS': 2,
    # points to remove per issue submitted that bot removed
    'BOT_CLOSED': 15,
    # points to add if user has blog
    'BLOG': 7,
    # points to add if issue has image
    'IMAGE': 15,
    # subtract if a needs reply label has been applied
    'AWAITING_REPLY': 125,
    # points to add per comment
    'COMMENT': 6,
    # points to add if codepen/plunkr is provided
    'DEMO': 20,

    # points to ADD for every FOLLOWERS_X followers
    'FOLLOWERS_ADD': 2,
    'FOLLOWERS_X': 5,

    # points to ADD for every CHAR_X characters in issue body
    'CHAR_ADD': 1,
    'CHAR_X': 200,

    # points added to each issue when created or updated
    # this decays quickly, so higher values mean age is more important
    'CREATED_START': 45,
    'UPDATE_START': 15,

}
