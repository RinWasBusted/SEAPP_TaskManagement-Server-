import requests
import os 
from ..models import db
from ..models.user_model import User
from werkzeug.security import check_password_hash, generate_password_hash
from .jwt_service import decode_google_token
import cloudinary.uploader
import uuid 
from flask_jwt_extended import create_access_token
import json

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


def getUserIDByEmail(email): 
    user_id = db.session.query(User.id).filter(email == User.email).first() 
    return str(user_id[0])  

def checkEmail(email):
    chk = db.session.query(1).filter(email == User.email).first() 
    if chk: return True 
    return False 

def updateUserById(id, name = None, email = None):
    user = User.query.get(id)

    if(user is None): return None
    if name is not None: 
        user.name = name
    if email is not None: 
        user.email = email  # Chi thuc hien update name va email 

    db.session.commit() 
    return {
        "id": id,
        "name": name if name is not None else None,
        "email": email if email is not None else None, 
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

def resetPassword(id, old_password, new_password):
    if(checkUser(id=id, password=old_password)):
        user = User.query.get(id)
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return {
            "success": True,
            "message": "Your password has been updated successfully.",
            "data": {
                "user": user.to_dict()
            }            
        }
    
    return {
        "success": False,
        "message": "Wrong password."
    }

def uploadAvatar(id, file='', url=''):
    try:
        user = User.query.get(id)
        if(file):
            if(user.avatar_url):
                cloudinary.uploader.destroy(user.avatar_url)
            upload_resutl = cloudinary.uploader.upload(file)
        if(url):
            if(user.avatar_url):
                cloudinary.uploader.destroy(user.avatar_url)
            upload_resutl = cloudinary.uploader.upload(url)
        user.avatar_url = upload_resutl['public_id']
        db.session.commit()
        user_data = user.to_dict()
        user_data['avatar_url'] = upload_resutl['secure_url']
        return {
            "success": True,
                "message": "Your avatar has been updated successfully.",
                "data": {
                    "user": user_data
                }
            }
    except Exception as e:
        return {
        "success": False,
        "message": "Failed to upload your avatar.",
        "error": f"{e}"
    }

def setNewPassword(id:int, new_password:str):
    user = User.query.get(id)
    if(user == None): 
        return None
    user.password = generate_password_hash(new_password)
    db.session.commit()
    return {
            "success": True,
            "message": "Your password has been updated successfully.",
            "data": {
                "user": user.to_dict()
            }            
        }

def getTokenFromCode(code): 
    url = 'https://oauth2.googleapis.com/token' 
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    } 
    data = {
        "code": code, 
        "client_id": os.environ.get('OAUTH_CLIENT_CLIENT_ID_2'), 
        "client_secret": os.environ.get('OAUTH_CLIENT_SECRET_2'), 
        'redirect_uri': 'http://localhost:5173', 
        'grant_type': 'authorization_code' 
    }
    r = requests.post(url , data=data , headers=headers) 
    if r: 
        return dict(r.json()).get('id_token') 
    return None 
def getUserInfoFromCode(code): 
    response_token_data = getTokenFromCode(code) 
    if not response_token_data: 
        return None 
    user_data = decode_google_token(response_token_data) 
    print(user_data) 
    if user_data:   #user_data duoc decode thanh cong  
        return user_data 
    return None  #user_data decode that bai 

def createSession(email , password): 
    user = checkUser(email = email, password = password)
    if user: 
        access_token = create_access_token(identity=str(user['id']), additional_claims={'jti': uuid.uuid4().hex})
        if isinstance(access_token, bytes):
            access_token = access_token.decode("utf-8")   #Chuyen doi ve lai thanh kieu du lieu str de JSON Serialize 
        return access_token 
    return None 
