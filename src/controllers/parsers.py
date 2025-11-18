from flask_restful import reqparse

# REGISTER PARSER
register_parser = reqparse.RequestParser()
register_parser.add_argument('name', type=str, required=True, help="Name cannot be blank", location='json')
register_parser.add_argument('email',type=str, required=True, help="Email cannot be blank", location='json' )
register_parser.add_argument('password', type=str, required=True, help="Password cannot be blank", location='json')


# LOGIN PARSER
login_parser = reqparse.RequestParser()
login_parser.add_argument('email',type=str, required=True, help="Email cannot be blank", location='json' )
login_parser.add_argument('password', type=str, required=True, help="Password cannot be blank", location='json')