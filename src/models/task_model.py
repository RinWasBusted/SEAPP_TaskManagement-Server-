from . import db

class TaskModel(db.Model):
    __tablename__ = 'tasks'
    
    # Các cột
    id = db.Column('task_id', db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column('desc', db.Text, nullable=True)
    due_time = db.Column(db.DateTime, nullable=True)
    important = db.Column(db.Boolean, default=False)
    urgent = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='To Do')
    
    # Khóa ngoại TeamID
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)
    # Relationship với Team
    team = db.relationship('TeamModel', backref=db.backref('tasks', lazy=True))
    # Mối quan hệ: Được Assign cho User (nhiều-nhiều) 
    # (đã được định nghĩa trong UserModel qua backref 'assignees')