from . import db

class InviteCode(db.Model):
    __tablename__ = 'invite_codes'
    
    # Các cột
    code = db.Column(db.String(50), primary_key=True)
    time_expired = db.Column(db.DateTime, nullable=False)
    
    # Khóa ngoại TeamID
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)

