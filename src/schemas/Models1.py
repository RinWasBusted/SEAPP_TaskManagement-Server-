from .. import db
class User(db.Model):
    __tablename__ = 'user'
    userID = db.Column(db.Integer , primary_key = True) 
    name = db.Column(db.String(50)) 
    age = db.Column(db.Integer) 
    def __init__(self , userID , name , age):
        self.userID = userID 
        self.name = name 
        self.age = age 