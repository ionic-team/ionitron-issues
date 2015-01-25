from main import db
import json


class IssueScore(db.Model):
    organization = db.Column(db.String(80), primary_key=True)
    repo = db.Column(db.String(80), primary_key=True)
    issue_number = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    title = db.Column(db.String(512))
    comments = db.Column(db.Integer)
    username = db.Column(db.String(512))
    created = db.Column(db.String(512))
    updated = db.Column(db.String(512))
    avatar = db.Column(db.String(512))
    score_data = db.Column(db.Text)
    assignee = db.Column(db.String(512))

    def __init__(self, organization, repo, issue_number):
        self.organization = organization
        self.repo = repo
        self.issue_number = int(issue_number)

    def __repr__(self):
        return '<IssueScore %r>' % self.issue_number

    def to_dict(self):
      score_data_dict = {}
      if self.score_data:
          score_data_dict = json.loads(self.score_data)

      return {
          'number': self.issue_number,
          'score': self.score,
          'title': self.title,
          'comments': self.comments,
          'username': self.username,
          'created': self.created,
          'updated': self.updated,
          'avatar': self.avatar,
          'score_data': score_data_dict,
          'assignee': self.assignee
      }


def get_issue(organization, repo, issue_number):
    return IssueScore.query.filter_by(organization=organization,
                                      repo=repo,
                                      issue_number=issue_number).first()

def get_issues(organization, repo):
    return IssueScore.query.filter_by(organization=organization, repo=repo)
