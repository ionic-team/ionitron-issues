from main import db


class IssueScore(db.Model):
    organization = db.Column(db.String(80), primary_key=True)
    repo = db.Column(db.String(80), primary_key=True)
    issue_number = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    data = db.Column(db.Text)

    def __init__(self, organization, repo, issue_number):
        self.organization = organization
        self.repo = repo
        self.issue_number = issue_number

    def __repr__(self):
        return '<IssueScore %r>' % self.number
