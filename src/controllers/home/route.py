from flask import Blueprint
from flask_restful import Api, Resource


home_bp = Blueprint('home' , __name__)

home_api = Api(home_bp)

class Home(Resource):
    def get(self):
        return 'Xin chao, day la noi dung dau tien'

home_api.add_resource(Home,'/')
