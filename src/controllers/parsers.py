from flask_restful import reqparse
from werkzeug.datastructures import FileStorage

# REGISTER PARSER
register_parser = reqparse.RequestParser()
register_parser.add_argument('name', type=str, required=True, help="Name cannot be blank", location='json')
register_parser.add_argument('email',type=str, required=True, help="Email cannot be blank", location='json' )
register_parser.add_argument('password', type=str, required=True, help="Password cannot be blank", location='json')


# LOGIN PARSER
login_parser = reqparse.RequestParser()
login_parser.add_argument('email',type=str, required=True, help="Email cannot be blank", location='json' )
login_parser.add_argument('password', type=str, required=True, help="Password cannot be blank", location='json')


# UPDATE USER
update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument('name', type=str, required=True, help="Name cannot be blank", location='json')
update_user_parser.add_argument('email',type=str, required=True, help="Email cannot be blank", location='json' )
update_user_parser.add_argument('password', type=str, required=True, help="Password cannot be blank", location='json')
update_user_parser.add_argument('avatar', type=list, location='files')

#CHANGE_NAME
change_name_parser = reqparse.RequestParser()
change_name_parser.add_argument('new_name', type=str, required=True, help="Name cannot be blank", location='json')


#CHANGE_EMAIL
change_email_parser = reqparse.RequestParser()
change_email_parser.add_argument('new_email',type=str, required=True, help="Email cannot be blank", location='json')
change_email_parser.add_argument('password', type=str, required=True, help="Password cannot be blank", location='json')

#RESET_PASSWORD
reset_password_parser = reqparse.RequestParser()
reset_password_parser.add_argument('old_password', type=str, required=True, help="Password cannot be blank", location='json')
reset_password_parser.add_argument('new_password', type=str, required=True, help="Password cannot be blank", location='json')

#UPLOAD_AVATAR
upload_avatar_parser = reqparse.RequestParser()
upload_avatar_parser.add_argument('avatar', type=FileStorage, location='files', required=True, help="You must upload an image")
