from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dotenv import load_dotenv
import os 

db = SQLAlchemy()

def db_config(app : Flask):
    # 1. Tải các biến môi trường
    load_dotenv()
    
    # 2. Thiết lập cấu hình DB (sử dụng biến toàn cục ở trên)
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    
    connStr = f"mariadb+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    app.config['SQLALCHEMY_DATABASE_URI'] = connStr
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 3. Liên kết db với app
    db.init_app(app)

    # Import models 
    from .association import team_member_association, assignment_association
    from .invite_code_model import InviteCode
    from .task_model import Task
    from .team_model import Team
    from .user_model import User

    

