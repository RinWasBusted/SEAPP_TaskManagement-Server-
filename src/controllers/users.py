from flask import Blueprint
from flask_restful import Api, Resource
from ..services.users_service import getUserFromId

users_bp = Blueprint('users', __name__)

users_api = Api(users_bp)

class Users(Resource):
    def get(self):
        user = getUserFromId(1)
        return user

users_api.add_resource(Users, '/')
