from flask import Flask 
from .config.dev_config import DevConfig
from dotenv import load_dotenv 
from .models import db, db_config
from flask_migrate import Migrate
import os
from datetime import timedelta
from flask_jwt_extended import JWTManager


def create_app(config_object=DevConfig):
    # Tải biến môi trường ngay khi hàm được gọi
    load_dotenv() 
    
    # Tạo đối tượng app BÊN TRONG hàm
    app = Flask(__name__)

    db_config(app)
    app.config.from_object(config_object)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

    migrate = Migrate(app, db)
    migrate.init_app(app, db)

    jwt = JWTManager(app)

    # 4. Đăng ký Blueprints/API ở đây
    from .api import api_bp
    app.register_blueprint(api_bp)

    # migrate.init_app(app, db)
    
    return app