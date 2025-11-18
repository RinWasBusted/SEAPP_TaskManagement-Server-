from . import db

class Team(db.Model):
    __tablename__ = 'teams'
    
    # Các cột
    id = db.Column('team_id', db.Integer, primary_key=True)
    icon_url = db.Column(db.String(255), nullable=True)
    banner_url = db.Column(db.String(255), nullable=True)
    name = db.Column('team_name', db.String(100), unique=True, nullable=False)
    description = db.Column('team_desc', db.String(500), nullable=True)
    
    # Khóa ngoại cho Leader và ViceLeader
    leader_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    vice_leader_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    
    # Mối quan hệ: Chứa các Task (1-nhiều)
    tasks = db.relationship('Task', backref='team', lazy=True)
    
    # Mối quan hệ: Chứa các InviteCode (1-nhiều)
    invite_codes = db.relationship('InviteCode', backref='team', lazy=True)
    
    # Relationship với leader và vice leader
    leader = db.relationship('User', foreign_keys=[leader_id], backref='led_teams')
    vice_leader = db.relationship('User', foreign_keys=[vice_leader_id], backref='vice_led_teams')