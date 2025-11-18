from flask import Blueprint
from flask_restful import Api, Resource

auth_bp = Blueprint('auth', __name__)
auth_api = Api(auth_bp)



# class Auth(Resource):
#     def post(self):

        

# auth_api.add_resource(Auth, '/auth/register')