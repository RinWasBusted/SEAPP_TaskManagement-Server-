from flask_restful import reqparse

register_parser = reqparse.RequestParser()
register_parser.add_argument('email',type=str, required=True, help="Email cannot be blank", location='json' )
register_parser.add_argument('password', type=str, required=True, help="Password cannot be blank")