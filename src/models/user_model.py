from . import db
from .association import team_member_association, assignment_association

class User(db.Model):
    __tablename__ = 'users'
    
    # Các cột
    id = db.Column('user_id', db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar_url": self.avatar_url,
        }
    
    def get_password(self):
        return self.password