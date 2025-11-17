from . import db
from .association import team_member_association, assignment_association

class UserModel(db.Model):
    __tablename__ = 'users'
    
    # Các cột
    id = db.Column('user_id', db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    
    # Mối quan hệ: Người dùng là Leader/ViceLeader của Team (1-nhiều)
    # Chúng ta dùng chuỗi 'TeamModel' để tránh circular import
    teams_leading = db.relationship('TeamModel', backref='leader', foreign_keys='TeamModel.leader_id', lazy=True)
    teams_vice_leading = db.relationship('TeamModel', backref='vice_leader', foreign_keys='TeamModel.vice_leader_id', lazy=True)
    
    # Mối quan hệ: Là thành viên của Team (nhiều-nhiều)
    teams = db.relationship('TeamModel', secondary=team_member_association, backref=db.backref('members', lazy=True))
    
    # Mối quan hệ: Được giao Task (nhiều-nhiều)
    assigned_tasks = db.relationship('TaskModel', secondary=assignment_association, backref=db.backref('assignees', lazy=True)) 