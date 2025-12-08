from flask_restful import reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest
import re 

# validate email format
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def validate_email_format(value):
    if not isinstance(value, str):
        raise BadRequest("Email field must be a string.")
    
    if not re.match(EMAIL_REGEX, value):
        raise BadRequest(value + " is not a valid email.")
    
    return value

# REGISTER PARSER
register_parser = reqparse.RequestParser()
register_parser.add_argument('name', type=str, required=True, help="Name cannot be blank", location='json')
register_parser.add_argument('email',type=validate_email_format, required=True, help="Email cannot be blank", location='json' )
register_parser.add_argument('password', type=str, required=True, help="Password cannot be blank", location='json')

# VERIFY PARSER
verify_parser = reqparse.RequestParser()
verify_parser.add_argument(
    'token', 
    type=str, 
    required=True, 
    help='Verification token is required in the URL query.',
    location='args' 
)

# LOGIN PARSER
login_parser = reqparse.RequestParser()
login_parser.add_argument('email',type=validate_email_format, required=True, help="Email cannot be blank", location='json' )
login_parser.add_argument('password', type=str, required=True, help="Password cannot be blank", location='json')

#LOGIN GOOGLE PAERSER 
login_google_parser = reqparse.RequestParser() 
login_google_parser.add_argument('code' , type= str, required = True, help = "Code cannot be blank" , location = "json") 

# UPDATE USER
update_user_parser = reqparse.RequestParser()
update_user_parser.add_argument('name', type=str, required=False, location='json')
update_user_parser.add_argument('email',type=validate_email_format, required=False, location='json' )

#CHANGE_NAME
change_name_parser = reqparse.RequestParser()
change_name_parser.add_argument('new_name', type=str, required=True, help="Name cannot be blank", location='json')


#CHANGE_EMAIL
change_email_parser = reqparse.RequestParser()
change_email_parser.add_argument('new_email',type=validate_email_format, required=True, help="Email cannot be blank", location='json')
change_email_parser.add_argument('password', type=str, required=True, help="Password cannot be blank", location='json')

#RESET_PASSWORD
reset_password_parser = reqparse.RequestParser()
reset_password_parser.add_argument('old_password', type=str, required=True, help="Password cannot be blank", location='json')
reset_password_parser.add_argument('new_password', type=str, required=True, help="Password cannot be blank", location='json')

#UPLOAD_AVATAR
upload_avatar_parser = reqparse.RequestParser()
upload_avatar_parser.add_argument('avatar', type=FileStorage, location='files', required=True, help="You must upload an image")

# FORGOT PASSWORD
forgot_password_parser = reqparse.RequestParser()
forgot_password_parser.add_argument('email',type=validate_email_format, required=True, help="Email cannot be blank", location='json')

#  SET_NEW_PASSWORD
set_new_password_parser = reqparse.RequestParser()
set_new_password_parser.add_argument('reset_password_token', type=str, required=True, help="Reset_password_token cannot be blank", location='json')
set_new_password_parser.add_argument('new_password', type=str, required=True, help="New password cannot be blank", location='json')

#Create Task
create_task_parser = reqparse.RequestParser()
create_task_parser.add_argument('title', type=str,
                                required=True, help="Task title cannot be blank", location='json')
create_task_parser.add_argument('description', type=str,
                                required=False, location='json')
create_task_parser.add_argument('dueTime', type=str,
                                required=True, help="Due time cannot be blank (e.g., 2025-11-20T17:00:00Z)", location='json')
create_task_parser.add_argument(
    'important',
    type=bool,
    required=False,
    location='json',
    help="Important flag must be boolean (true/false)"
)

create_task_parser.add_argument(
    'urgent',
    type=bool,
    required=False,
    location='json',
    help="Urgent flag must be boolean (true/false)"
)

create_task_parser.add_argument('assigneeIds', type=str,
                                required=False, location='json', action='append')

#update task
update_task_parser = reqparse.RequestParser()
update_task_parser.add_argument('title', type=str,
                                required=False, location='json')
update_task_parser.add_argument('description', type=str,
                                required=False, location='json')
update_task_parser.add_argument('dueTime', type=str,
                                required=False, location='json')
update_task_parser.add_argument(
    'important',
    type=bool,
    required=False,
    location='json'
)
update_task_parser.add_argument(
    'urgent',
    type=bool,
    required=False,
    location='json'
)
update_task_parser.add_argument(
    'status',
    type=str,
    choices=('to do', 'in progress', 'completed'),
    required=False,
    location='json'
)

#search task
search_tasks_parser = reqparse.RequestParser()
search_tasks_parser.add_argument('q', type=str,
                                required=True, help="Search query 'q' cannot be blank", location='args')
search_tasks_parser.add_argument('teamId', type=str,
                                required=False, location='args')
search_tasks_parser.add_argument(
    'status',
    type=str,
    choices=('to do', 'in progress', 'completed'),
    required=False,
    location='args'
)
search_tasks_parser.add_argument(
    'important',
    type=bool,
    required=False,
    location='args'
)
update_task_parser.add_argument(
    'urgent',
    type=bool,
    required=False,
    location='json'
)

# CREATE NEW TEAM 
create_new_team_parser = reqparse.RequestParser() 
create_new_team_parser.add_argument("icon" , type=FileStorage, required = False, location='files') 
create_new_team_parser.add_argument("banner" , type=FileStorage , required = False , location = 'files') 
create_new_team_parser.add_argument("teamName", type = str , required = True , help = 'Missing name' , location = 'form') 
create_new_team_parser.add_argument("teamDescription" , type = str , required = False , location = 'form') 

# UPDATE THE TEAM 
update_team_parser = reqparse.RequestParser() 
update_team_parser.add_argument("icon" , type=FileStorage , required = False , location='files') 
update_team_parser.add_argument("banner" , required = False , type = FileStorage , location = 'files') 
update_team_parser.add_argument("teamName" , required = False , type=str , location = 'form') 
update_team_parser.add_argument("teamDescription" , required = False , type = str , location = 'form') 
update_team_parser.add_argument("leaderID" , required = False , type = int , location = 'form') 
update_team_parser.add_argument("viceLeaderID" , required = False , type = int , location = 'form') 

#User leave the group 
user_leave_parser = reqparse.RequestParser() 
user_leave_parser.add_argument("teamID" , type = int , required = True , help = "Missing team-leave id" , location = 'json')

#Leader kich members =)) 
leader_kick_parser = reqparse.RequestParser() 
leader_kick_parser.add_argument("teamID" , type = int , required = True , help = "Missing team-leave id" , location = 'json') 
leader_kick_parser.add_argument("userID" , type = int , required = True , help = "Missing member to kick" , location = 'json')

# GET TEAM ROLE 
user_role_parser = reqparse.RequestParser() 
user_role_parser.add_argument('teamID' , type = int , required = True , help = "Missing team to get role" , location = "args")

# GET TEAM CODE 
team_code_parser = reqparse.RequestParser()  
team_code_parser.add_argument('teamID' , type = int , required = True , help = "Missing team to get code" , location = 'args')

# CREATE NEW TEAM CODE 
create_new_team_code_parser = reqparse.RequestParser() 
create_new_team_code_parser.add_argument('teamID' , type = int , required = True , help = "Missing team" , location = 'json') 

# Search a task 
search_task_by_name = reqparse.RequestParser() 
search_task_by_name.add_argument('searchText' , type = str, required = False , location = 'json') 