from flask import Blueprint
from flask_restful import Api, Resource
from .parsers import register_parser, login_parser
from werkzeug.security import generate_password_hash
from ..services.users_service import createUser, getUserByEmail, checkUser
from flask_jwt_extended import create_access_token


auth_bp = Blueprint('auth', __name__)
auth_api = Api(auth_bp)


class Register(Resource):
    def post(self):
        register_args = register_parser.parse_args()
        name = register_args['name']
        email = register_args['email']
        password = generate_password_hash(register_args['password'])

        if(getUserByEmail(email)):
            return {
                "status": "error",
                "message": "Registration failed. The email provided is already in use.",
                "data": None
            }, 409

        new_user = createUser(name, email, password)

        if(new_user):
            access_token = create_access_token(identity=new_user['email'])
            
            return {
                "status": "success",
                "message" : "User register successfully.",
                "data": {
                    "user": new_user
                    
                },
                "tokens": {
                    "access_token": access_token,
                    "token_type": "Bearer", 
                    "expires_in": 60*60*24*7,
                }
            }, 201
        else:
            return {
                "status": "error",
                "message": "Unknown error."
            }, 400
            

class Login(Resource):
    def post(self):
        login_args = login_parser.parse_args()
        email = login_args['email']
        password = login_args['password']

        user = checkUser(email, password)
        if(user):
            access_token = create_access_token(identity=user['email'])
            
            return {
                "status": "success",
                "message" : "Login successful.",
                "data": {
                    "user": user
                },
                "tokens": {
                    "access_token": access_token,
                    "token_type": "Bearer", 
                    "expires_in": 60*60*24*7,
                }
            }, 200
        
        return {
            "status": "error",
            "message": "Invalid credentials provided.",
            "data": None
        }, 401


auth_api.add_resource(Register, '/register')
auth_api.add_resource(Login, '/login')