from . import db

team_member_association = db.Table('team_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('teams.team_id'), primary_key=True)
)

assignment_association = db.Table('assignments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.task_id'), primary_key=True)
)