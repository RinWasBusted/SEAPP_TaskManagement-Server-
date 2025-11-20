from flask import Blueprint
from flask_restful import Api, Resource
from ..services.users_service import getUserById
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__)

users_api = Api(users_bp)

class Users(Resource):
    @jwt_required()
    def get(self, data):
        userId = get_jwt_identity()
        user = getUserById(userId)
        return user



users_api.add_resource(Users, '/users/me')
