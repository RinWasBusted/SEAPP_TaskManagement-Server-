from . import db
from datetime import datetime


class TeamCreateJoinCodeModel(db.Model):
    __tablename__ = 'team_create_join_code'

    # Khóa chính composite
    team_id = db.Column(db.Integer, db.ForeignKey('invite_codes.team_id', ondelete='CASCADE'), primary_key=True)
    code = db.Column(db.String(50), db.ForeignKey('invite_codes.code', ondelete='CASCADE'), primary_key=True)

    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship với Team (qua InviteCode)
    invite_code = db.relationship('InviteCodeModel', backref=db.backref('create_history', lazy=True))

    # Relationship với User
    creator = db.relationship('UserModel', backref=db.backref('created_joincodes', lazy=True))