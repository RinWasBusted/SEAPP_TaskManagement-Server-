import os 
from flask import Flask 
from dotenv import load_dotenv 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv() 
db = SQLAlchemy() 

def create_app(): 
    app = Flask(__name__) 
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    db.init_app(app) 
    migrate = Migrate() 
    migrate.init_app(app , db) 
    
    #Noi dang ki cac blue prints 
    from .api import configure_api_bp 
    app.register_blueprint(configure_api_bp(app , db)) 
    return app 