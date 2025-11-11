from flask import Blueprint
from .controllers.home.route import home_bp

api_bp = Blueprint('api' , __name__)

#Dang ki du lieu cho cac route  
api_bp.register_blueprint(home_bp) 