from ..models import db
from ..models.user_model import User
from werkzeug.security import check_password_hash

def createUser(name:str, email:str, password:str):
    new_user = User(name=name, email=email, password=password )
    db.session.add(new_user)
    db.session.commit()
    return new_user.to_dict()

def getUserById(userId : int):
    user = db.session.get(User, userId)
    return user.to_dict()

def getUserByEmail(email:str):
    user = db.session.execute(
        db.select(User).filter_by(email = email)
    ).scalar_one_or_none()

    if user:
        return user.to_dict()
    return None

def checkUser(email:str, password:str):
    user = db.session.execute(
        db.select(User).filter_by(email = email)
    ).scalar_one_or_none()
    
    if(not user):
        return None
    
    if(check_password_hash(user.get_password(), password)):
        return user.to_dict()
    
    return None

