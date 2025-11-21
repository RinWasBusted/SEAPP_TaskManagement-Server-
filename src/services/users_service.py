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

def checkUser(id:int = -1, email:str = "", password:str = ""):
    if(email != ""):
        user = db.session.execute(
            db.select(User).filter_by(email = email)
        ).scalar_one_or_none()
        
        if(not user):
            return None
        
        if(check_password_hash(user.get_password(), password)):
            return user.to_dict()
    elif(id >= 0):
        user = User.query.get(id)
        if(not user):
            return None
        
        if(check_password_hash(user.get_password(), password)):
            return user.to_dict()
    return None


def updateUserById(id, name, email, password, avatar_url):
    user = User.query.get(id)

    if( user is None): return None

    user.name = name
    user.email = email
    user.password = password
    user.avatar_url = avatar_url

    db.session.commit() 
    
    return {
        "id": id,
        "name": name,
        "password": password,
        "avatar_url": avatar_url
    }

def changeEmail(id, new_email, password):
    if(getUserByEmail(new_email)): return {
        "success": False,
        "message": "New email are already exists."
    }

    if(checkUser(id = id, password=password)):
        user = User.query.get(id)
        user.email = new_email
        db.session.commit()
        return {
            "success": True,
            "message": "Your email address has been successfully changed.",
            "data": {
                "user": user.to_dict()
            }            
        }
    
    return {
        "success": False,
        "message": "Wrong password."
    }

def changeName(id, new_name):
    user = User.query.get(id)
    if(user):
        user.name = new_name
        db.session.commit()
        return {
            "success": True,
            "message": "Your name has been successfully changed.",
            "data": {
                "user": user.to_dict()
            }            
        }
    
    return {
        "success": False,
        "message": "User not found."
    }