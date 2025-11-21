from flask import Blueprint
from flask_restful import Api, Resource
from ..services.users_service import getUserById, updateUserById, changeEmail, changeName
from flask_jwt_extended import jwt_required, get_jwt_identity
from .parsers import update_user_parser, change_email_parser, change_name_parser, reset_password_parser, upload_avatar_parser
import cloudinary
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user', __name__)

user_api = Api(user_bp)

class User(Resource):
    @jwt_required()
    def get(self):
        userId = int(get_jwt_identity())
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
    def put(self):
        userId = int(get_jwt_identity())

        args = update_user_parser.parse_args()

        name = args['name']
        email = args['email']
        password = generate_password_hash(args['password'])
        file = args['avatar']

        if(file == ''):
            return {
            "success": False,
            "message": "There is no selected file"
        } 

        try:
            avatar_url = cloudinary.uploader.upload(file)

        except Exception as e:
            return {
                "success": False,
                "message": f"{e}"
            }

        if(updateUserById(id=userId, name=name, email=email, password=password, avatar_url=avatar_url)):
            return {
                "success": True,
                "message": "User updated successfully.",
                "data": {
                    "user": {
                        "name": name,
                        "email": email,
                        "avatar_url": avatar_url
                    }
                }  
            }
        else:
            return {
                "success": False,
                "message": "Failed to update user"
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









user_api.add_resource(User, '/')
user_api.add_resource(ChangeEmail, '/change-email')
user_api.add_resource(ChangeName, '/change-name')
