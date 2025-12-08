from flask import Response, request
from flask_restful import Api, Resource
from flask import Blueprint
from ..models.team_model import Team
from ..models.user_model import User
from ..models.invite_code_model import InviteCode
from ..models.task_model import Task
from ..models.association import team_member_association , assignment_association
from ..models import db
from flask_jwt_extended import jwt_required , get_jwt_identity
from ..services.teams_service import queryTeam , createCodeForTeam , getTeamByID
from ..utils import getImageUrl
from ..services.teams_service import uploadTeamImage, isUserMember, addMemberToTeam, getTeamCode

from .parsers import create_new_team_parser, update_team_parser  , user_leave_parser , leader_kick_parser, user_role_parser , team_code_parser , create_new_team_code_parser
from ..services.teams_service import update_team, delete_team, isUser, isLeader , isViceLeader ,  deleteUserFromGroup , createNewTeamCode


# Phai import theo kieu relative path ntn, bo dau . o dau di thi se thanh absolute path

team_bp = Blueprint('team' , __name__)
team_api = Api(team_bp)

class Teams(Resource):
    # 1. Lay thong tin ve 1 team
    @jwt_required()
    def get(self, id = None): # Viet 1 ham thoi, khong duoc phep co 2 ham
        #cung ten trong Python, du cho khac danh sach tham so
        # Lay thong tin cu the ve 1 team
        if id is None:
            return {
                "scuesss": False,
                "message": "Don't know team to get information"
            } , 400  # Bad request
        userID = int(get_jwt_identity())
        chk = isUser(userID)
        if not chk:
            return {
                "success": False,
                "message": "User not found",
            } , 400 # Bad request
        chk = isUserMember(userID , id)
        if not chk:
            return {
                "success": False, 
                "message": "User is not a member of this team" 
            } , 400 
        response_data = getTeamByID(id , userID=userID) # Lat nua code tiep tai day 
        return response_data
        
    # 2. Tao team moi 
    @jwt_required() 
    def post(self):   # Da check 
        current_user_id = int(get_jwt_identity()) 
        if not(current_user_id): 
            return {
                "success": False,
                "message": "Can't read information from token"
            }, 401
        #Lay cac thong tin tu trong data gui ve
        if not(isUser(current_user_id)):
            return {
                "success": False,
                "message": "User not found"
            } , 401

        data = dict(create_new_team_parser.parse_args())
        name = data.get('teamName')
        icon = data.get('icon')
        banner = data.get('banner')
        description = data.get('description')

        # Tao team moi
        new_team = Team()
        new_team.name = name
        new_team.description = (description if description else '')
        new_team.leader_id = current_user_id
        new_team.leader = db.session.query(User).filter(User.id == current_user_id).first()
        new_team.banner_url = None
        new_team.icon_url = None
        print(icon , banner)
        if icon:
            url = uploadTeamImage(new_team , icon.read() , 'icon')
            if not(url):
                new_team.icon_url = None
        else:
            new_team.icon_url = None
        if banner:
            url = uploadTeamImage(new_team , banner.read() , 'banner')
            if not(url):
                new_team.banner_url = None
        else:
            new_team.banner_url = None

        db.session.add(new_team)
        db.session.commit()

        # Goi ham de tao ma code
        code = createCodeForTeam(new_team.id , 604800) # Tao ma code de tham gia nhom

        # Them du lieu current_user_id , team_id vao ben trong bang association
        stmt = team_member_association.insert().values(
                team_id = new_team.id,
                user_id = current_user_id
            )
        db.session.execute(stmt)
        db.session.commit() 
        return {
            "success": True,
            "message": "Your team has been completed successfully. You can join with the code below",
            "data": queryTeam(new_team.id),
            "code": code
        } , 201
    #Update team
    @jwt_required()
    def put(self, id = None): #id = teamID
        userID = int(get_jwt_identity())
        if not userID:
            return {
                "success": False,
                "message": "Your token is failed to make any updated"
            } , 401
        if not isUser(userID):
            return {
                "success": False,
                "message": "User not found"
            } , 401
        team = db.session.query(Team.leader_id , Team.vice_leader_id).filter(Team.id == id).first()   # Query ra hai cai nay de hoi
        if not team:
            return {
                "success": False,
                "message": "Don't know team to update"
            } , 401
        if userID == int(team[0]) or (team[1] and userID == int(team[1])): # Neu nhu userID kong phai la leader_id hay vice_leader_id
            data = update_team_parser.parse_args()
            response_data = update_team(userID , id , data)
            return response_data
        else:
            return {
                "success": False,
                "message": "You don't have any permission to do this action"
            } , 403

    @jwt_required()
    def delete(self , id):
        current_user_id = int(get_jwt_identity())
        information = db.session.query(Team.leader_id).filter(id == Team.id).first()

        # Khong tim thay team
        if not information:
            return {
                "success": False,
                "message": "Team not found to delete"
            } , 400
        # Chi co leader moi duoc xoa team
        if int(information[0]) != current_user_id:
            return {
                "success": False,
                "message": "You dont have permission to do this action"
            } , 403

        response_data = delete_team(id)
        return response_data , 200

# Tien hanh join team
class TeamJoinCode(Resource):
    # Tao code cho team
    def post(self, id): # Da check
        time = request.json.get('expiresIn')
        if time is None:
            return {
                "Success": False,
                "message": "Missing time to create team code"
            } , 400
        print(id , time)
        if id is None:
            return {
                "Success": False,
                "Message": "Team not found"
            } , 400
        code = createCodeForTeam(id , int(time))
        print(code)
        if code is None:
            return {
                "Success": False,
                "message": "Missing information to create team code"
            } , 401
        return {
            "success": True,
            "message": "You can use the code below to join",
            "data": {
                "teamID": id, 
                "code": code 
            } 
        } , 201 
class TeamCode(Resource): 
    @jwt_required() 
    def get(self): 
        current_user_id = int(get_jwt_identity()) 
        if current_user_id is None: 
            return {
                "success": False, 
                "message": "Code is invalid"
            } , 401 
        team_id = team_code_parser.parse_args().get('teamID') 
        chk = isUserMember(userID=current_user_id , teamID=team_id) 
        if not chk: 
            return {
                "success": False, 
                "message": "You don't belong to this team"
            }, 401 
        code = getTeamCode(team_id) 
        return {
            "success": True, 
            "code": code 
        }
    @jwt_required() 
    def post(self): 
        current_user_id = int(get_jwt_identity()) 
        if current_user_id is None: 
            return {
                "success": False, 
                "message": "Code is invalid"
            } , 401 
        data = dict(create_new_team_code_parser.parse_args())
        team_id = data.get('teamID') 
        print(team_id) 
        is_lead = isLeader(user_id=current_user_id , team_id=team_id) 
        is_vice_lead = isViceLeader(user_id=current_user_id , team_id = team_id) 
        if is_lead or is_vice_lead: 
            code = createNewTeamCode(team_id)
            return {
                "success": True, 
                "message": "This is the new code for your team", 
                "code": code 
            }
        return {
            "success": False, 
            "message": "You don't have enough permission", 
        } , 403 


# Tham gia nhom
# Yeu cau phai co jwt de tien hanh join nhom
class TeamJoin(Resource):
    @jwt_required() # Da check
    def post(self):
        current_user_id = int(get_jwt_identity())
        if not current_user_id:
            return {
                "success": False,
                "message": "User not identity"
            } , 401

        data = request.json
        code = data.get('code')

        teamID = db.session.query(InviteCode.team_id).filter(code == InviteCode.code).first() #Boc them dieu kien keim tra code phai con han

        if not teamID:
            return {
                "success": False,
                "message": "Your code has been expired or incorrect"
            } , 401
        teamID = int(teamID[0])

        chk = isUserMember(current_user_id , teamID)
        if chk:
            return {
                "success": False,
                "message": "You has been a member of this team"
            }

        addMemberToTeam(current_user_id , teamID)
        return {
            "sucess": True,
            "message": "You have been joined successfully"
        } ,200

        # Tien hanh kiem tra xem day co phai thanh vien cua team hay khong

class UserWithTeam(Resource):
    @jwt_required()
    def get(self): # Da check -> Lay tat ca cac team ma user nay da tham gia
        current_user_id = int(get_jwt_identity())
        if not current_user_id:
            return {
                "success": False,
                "message": "User not found to get all teams"
            } , 401
        if not isUser(current_user_id):
            return {
                "success": False,
                "message": "User not found"
            } , 401
        teams = db.session.query(Team.id , Team.name , Team.banner_url , Team.icon_url , Team.description , Team.leader_id , Team.vice_leader_id).join(team_member_association , team_member_association.c.team_id == Team.id).filter(current_user_id == team_member_association.c.user_id).all()
        teams = [
            {
                "id": teamID,
                "name": name,
                "banner": getImageUrl(banner),
                "icon": getImageUrl(icon),
                "leader_id": leader,
                "vice_leader_id": vice_leader,
                "description": description
            }
            for teamID, name, banner , icon, description , leader , vice_leader  in teams
        ]
        return {
            "success": True,
            "message": "This is all teams you joined",
            "teamData": teams
        } , 200
    # Nguoi dung roi group
    @jwt_required()
    def delete(self):
        current_user_id = int(get_jwt_identity())
        teamID = user_leave_parser.parse_args().get('teamID')
        if not isUserMember(current_user_id , teamID):
            return {
                "success": False,
                "message": "You don't belong to this group"
            } , 400
        if isLeader(current_user_id , teamID):
            return {
                "success": False,
                "message": "Leader cannot leave the group"
            } , 403
        deleteUserFromGroup(current_user_id , teamID)
        return {
            "success": True,
            "message": "You have leaved group successfully"
        } , 200

class TeamRole(Resource): 
    @jwt_required() 
    def get(self): 
        current_user_id = int(get_jwt_identity()) 
        if not current_user_id: 
            return {
                "success": False, 
                "message": "Invalid token or id" 
            } , 200 
        data = user_role_parser.parse_args() 
        teamID = data.get('teamID') 
        if not teamID: 
            return {
                "success": False, 
                "message": "Team not found"
            } , 200 
        chk = isUserMember(current_user_id , teamID) 
        if not chk: 
            return {
                "success": False, 
                "message": "You dont belong to this team"
            } , 200 
        leader_id = db.session.query(Team.leader_id).filter(teamID == Team.id).first() 
        vice_leader_id = db.session.query(Team.vice_leader_id).filter(teamID == Team.id).first() 
        if leader_id[0] == current_user_id: 
            return {
                "success": True, 
                "role": "leader" 
            } 
        if vice_leader_id[0] == current_user_id: 
            return {
                "success": True, 
                "role": "vice" 
            } 
        return {
            "success": True, 
            "role": "member" 
        }


class LeaderKickUser(Resource):
    @jwt_required()
    def delete(self):
        current_user_id = int(get_jwt_identity())
        if not isLeader(current_user_id):
            return {
                "success": False,
                "message": "You don't have permission to do this action"
            }
        data = leader_kick_parser.parse_args()
        teamID = data.get('teamID')
        userID = data.get('userID')
        if not(teamID) or not(userID):
            return {
                "success": False ,
                "message": "Missing information to delete"
            } , 401
        if not(isUserMember(userID , teamID)):
            return {
                "success": False,
                "message": "This user don't belong to your group"
            } , 400
        deleteUserFromGroup(userID , teamID)
        return {
            "success": True,
            "message": "Kick successfully"
        }
team_api.add_resource(Teams , '/' , '/<int:id>')
team_api.add_resource(UserWithTeam , '/user')
team_api.add_resource(TeamJoinCode , '/<int:id>/join-code')
team_api.add_resource(TeamJoin , '/join')
team_api.add_resource(TeamRole , '/role')
team_api.add_resource(TeamCode , '/code/team')
