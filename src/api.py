from flask import Blueprint
from .controllers.home.route import home_bp
from .controllers.users import users_bp
from .controllers.auth import auth_bp

api_bp = Blueprint('api' , __name__)

#Dang ki du lieu cho cac route  
api_bp.register_blueprint(home_bp, url_prefix = '/home')
api_bp.register_blueprint(users_bp, url_prefix = '/users') 
api_bp.register_blueprint(auth_bp, url_prefix = '/auth')