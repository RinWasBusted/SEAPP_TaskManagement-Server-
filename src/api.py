from flask import Blueprint
from .controllers.home.route import configure_home_bp

def configure_api_bp(app , db): 
    api_bp = Blueprint('api' , __name__) 
    #Dang ki du lieu cho cac route  
    api_bp.register_blueprint(configure_home_bp(app , db)) 
    
    
    return api_bp 
