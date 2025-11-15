from flask import Blueprint 
from flask_sqlalchemy import SQLAlchemy
from src.schemas.Models import User , Blog 
from flask_sqlalchemy import session # Dung cai nay de thao tac voi ORM 

def configure_home_bp(app , db : SQLAlchemy): 
    home_bp = Blueprint('home' , __name__) 
    @home_bp.route('/' , methods = ['GET']) 
    def home_get(): 
        # Them du lieu vao database: 
        db.session.add(User(1 , 'An' , 18)) 
        db.session.add(User(2 , 'Thai' , 18)) 
        db.session.add(User(3 , 'Hung' , 18)) 
        db.session.add(User(4, 'Thien' , 18))
        db.session.commit() 
        return 'Xin chao cac ban, day la noi dung dau tien' 
    return home_bp
