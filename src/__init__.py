from flask import Flask 
from .config.dev_config import DevConfig
from .config.cloudinary_config import cloudinary_config
from .config.mail import mail_config
from dotenv import load_dotenv 
from .models import db, db_config
from flask_migrate import Migrate
import os
from datetime import timedelta
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message
from .extensions import jwt_blacklist


def create_app(config_object=DevConfig):
    # Tải biến môi trường ngay khi hàm được gọi
    load_dotenv() 
    
    # Tạo đối tượng app BÊN TRONG hàm
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')

    app.config.from_object(config_object)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

    db_config(app)

    migrate = Migrate(app, db)
    migrate.init_app(app, db)

    jwt = JWTManager(app)
    @jwt.token_in_blocklist_loader
    def check_jwt_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload.get('jti')
        if(jwt_blacklist is None): return False

        is_blacklisted = jwt_blacklist.get(jti)

        if(is_blacklisted): return True
        
        return False



    cloudinary_config()

    oauth = OAuth(app)
    google = oauth.register(
        name = 'google',
        client_id = os.getenv('OAUTH_CLIENT_ID'),
        client_secret = os.getenv('OAUTH_CLIENT_SECRECT'),
        server_metadata_uri = 'https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs = {'scope':'openid profile email'} 
    ) 

    mail_config(app)

    # 4. Đăng ký Blueprints/API ở đây
    from .api import api_bp
    app.register_blueprint(api_bp)

    # migrate.init_app(app, db)
    
    return app