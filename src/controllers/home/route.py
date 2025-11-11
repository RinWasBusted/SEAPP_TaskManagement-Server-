from flask import Blueprint

home_bp = Blueprint('home' , __name__) 

@home_bp.route('/') 
def home_get(): 
    return 'Xin chao, day la noi dung dau tien'