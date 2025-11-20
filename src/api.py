from flask import Blueprint
from .controllers.home.route import home_bp
from .controllers.user import user_bp
from .controllers.auth import auth_bp

api_bp = Blueprint('api' , __name__)

#Dang ki du lieu cho cac route  
api_bp.register_blueprint(home_bp, url_prefix = '/home')
api_bp.register_blueprint(user_bp, url_prefix = '/user') 
api_bp.register_blueprint(auth_bp, url_prefix = '/auth')