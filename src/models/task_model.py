from . import db

class Task(db.Model):
    __tablename__ = 'tasks'
    
    # Các cột
    id = db.Column('task_id', db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column('desc', db.Text, nullable=True)
    due_time = db.Column(db.DateTime, nullable=True)
    important = db.Column(db.Boolean, default=False)
    urgent = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='to do')
    
    # Khóa ngoại TeamID
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)
    def to_dict(self): 
        return {
            "taskID": self.id, 
            "title": self.title, 
            "description": self.description, 
            "dueTime": self.due_time, 
            "priority": [self.important , self.urgent], 
            "status": self.status, 
            #Them cot creaatedAt sau 
         }
    def to_dict_to_send(self): 
        return {
            "taskID": self.id, 
            "title": self.title, 
            "description": self.description, 
            "dueTime": str(self.due_time), 
            "priority": [self.important , self.urgent], 
            "status": self.status, 
            #Them cot creaatedAt sau 
         }