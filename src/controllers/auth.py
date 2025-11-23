from flask import Blueprint, url_for, current_app
from flask_restful import Api, Resource
from .parsers import register_parser, login_parser
from werkzeug.security import generate_password_hash
from ..services.users_service import createUser, getUserByEmail, checkUser, uploadAvatar
from flask_jwt_extended import create_access_token
import os
from dotenv import load_dotenv 
import secrets


load_dotenv()
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
                "success": "error",
                "message": "Registration failed. The email provided is already in use.",
                "data": None
            }, 409

        new_user = createUser(name, email, password)

        if(new_user):
            access_token = create_access_token(identity=str(new_user['id']))
            
            return {
                "success": True,
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
                "success": False,
                "message": "Unknown error."
            }, 400
            

class Login(Resource):
    def post(self):
        login_args = login_parser.parse_args()
        email = login_args['email']
        password = login_args['password']

        user = checkUser(email = email, password = password)
        if(user):
            access_token = create_access_token(identity=str(user['id']))
            
            return {
                "success": True,
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
            "success": False,
            "message": "Invalid credentials provided.",
            "data": None
        }, 401
    
class LoginGoogle(Resource):
    def get(self):
        try:
            state = secrets.token_urlsafe(32)
            session['oauth_state'] = state
            redirect_uri = url_for('authorizegoogle', _external=True)
            return google.authorize_redirect(redirect_uri, state)
        except Exception as e:
            current_app.logger.error(f"Error during login:{str(e)}")
            return {
                "success": False,
                "message": "Unable to initiate Google login."
            }, 500

class AuthorizeGoogle(Resource):
    def get(self):
        try:
            # Xác thực state token (CSRF protection)
            state = request.args.get('state')
            if not state or state != session.get('oauth_state'):
                    raise Unauthorized("Invalid state parameter")    

            # Xóa state sau khi dùng
            session.pop('oauth_state', None)
                    
            token = google.authorize_access_token()
            if not token:
                raise BadRequest("Failed to obtain access token")
            
            userinfo_endpoint = google.server_metadata['userinfo_endpoint']
            if not userinfo_endpoint:
                raise BadRequest("Userinfo endpoint not available")

            resp = google.get(userinfo_endpoint)
            if resp.status_code != 200:
                raise BadRequest("Failed to fetch user info from Google")

            user_info = resp.json()
            email = user_info['email']

            user = getUserByEmail(email)
            user['login_method'] = 'google'

            if(user):
                access_token = create_access_token(identity=user['id'], additional_claims={'login_method': 'google'})

                return {
                    "success": True,
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
            
            name = user_info['name']
            picture = user_info['picture']
            sub_id = user_info['sub']
            
            user = createUser(name=name, email=email, password = sub_id)
            uploadAvatar(id=user['id'], url=picture)
            access_token = create_access_token(identity=user['id'], additional_claims={'login_method': 'google'})
            return {
                    "success": True,
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
        except Unauthorized as e:
            current_app.logger.warning(f"Unauthorized Google login attempt: {str(e)}")
            return {
                "success": False,
                "message": "Unauthorized access."
            }, 401
            
        except BadRequest as e:
            current_app.logger.error(f"Bad request during Google auth: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }, 400
            
        except Exception as e:
            current_app.logger.error(f"Unexpected error during Google auth: {str(e)}")
            return {
                "success": False,
                "message": "An error occurred during login."
            }, 500

            

        

auth_api.add_resource(Register, '/register')
auth_api.add_resource(Login, '/login')
auth_api.add_resource(LoginGoogle, '/login-google')
auth_api.add_resource(AuthorizeGoogle, '/authorize-google')