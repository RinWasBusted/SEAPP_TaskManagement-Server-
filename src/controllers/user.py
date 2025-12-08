from flask import Blueprint
from flask_restful import Api, Resource
from ..services.users_service import getUserById, updateUserById, changeEmail, changeName, resetPassword, uploadAvatar
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .parsers import update_user_parser, change_email_parser, change_name_parser, reset_password_parser, upload_avatar_parser
import cloudinary
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user', __name__)

user_api = Api(user_bp)

class User(Resource):
    @jwt_required()
    def get(self):
        userId = int(get_jwt_identity())
        print(userId) 
        if(userId):
            user = getUserById(userId)
            return {
                "success": True,
                "data": {
                    "user": user
                }
            }
        
        return {
            "success": False,
            "data": None
        }
    @jwt_required() 
    def post(self): 
        userID = int(get_jwt_identity()) 
        if userID: 
            data = update_user_parser.parse_args() 
            name = data.get('name') 
            email = data.get('email') 
            response_data = updateUserById(userID , name = name , email = email)
            if response_data: 
                return {
                    "success": True, 
                    "message": "Update information successfully", 
                    "data": response_data 
                } 
            return {
                "sucess": False, 
                "message": "User not found"
            }
        return {
            "success": False, 
            "message": "Invalid token"
        }


class ChangeEmail(Resource):
    @jwt_required()
    def patch(self):
        id = int(get_jwt_identity())
        args = change_email_parser.parse_args()

        new_email = args['new_email']
        password = args['password']
        
        result = changeEmail(id = id, new_email=new_email, password=password)
        
        return result

class ChangeName(Resource):
    @jwt_required()
    def patch(self):
        id = int(get_jwt_identity())
        
        args = change_name_parser.parse_args()
        new_name = args['new_name']

        result = changeName(id=id, new_name=new_name)
        
        return result

class ResetPassword(Resource):
    @jwt_required()
    def patch(self):
        id = int(get_jwt_identity())
        claims = get_jwt() 
        login_method = claims.get('login_method')
        args = reset_password_parser.parse_args()
        old_password = args['old_password']
        new_password = args['new_password']

        result = resetPassword(id=id, old_password=old_password, new_password=new_password , login_method=login_method)

        return result

class UploadAvatar(Resource):
    @jwt_required()
    def patch(self):
        id = int(get_jwt_identity())

        args = upload_avatar_parser.parse_args()
        avatar = args['avatar']

        result = uploadAvatar(id=id, file=avatar)

        return result



user_api.add_resource(User, '/')
user_api.add_resource(ChangeEmail, '/change-email')
user_api.add_resource(ChangeName, '/change-name')
user_api.add_resource(ResetPassword, '/reset-password')
user_api.add_resource(UploadAvatar, '/upload-avatar')