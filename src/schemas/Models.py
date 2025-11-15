from .. import db 
class Blog(db.Model):
    __tablename__ = 'blog'
    blogID = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))  
    content = db.Column(db.String(1000))
    authorID = db.Column(db.Integer, db.ForeignKey('user.userID'))
    author = db.relationship('User')
    def __init__(self , blogID , title , content , authorID): 
        self.title = title 
        self.content = content
        self.blogID = blogID 
        self.authorID = authorID

class User(db.Model):
    __tablename__ = 'user'
    userID = db.Column(db.Integer , primary_key = True) 
    name = db.Column(db.String(50)) 
    age = db.Column(db.Integer) 
    def __init__(self , userID , name , age):
        self.userID = userID 
        self.name = name 
        self.age = age 