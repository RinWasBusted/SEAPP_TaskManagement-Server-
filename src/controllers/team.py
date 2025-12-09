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
from ..extensions import logger

from .parsers import create_new_team_parser, update_team_parser  , user_leave_parser , leader_kick_parser, user_role_parser , team_code_parser , create_new_team_code_parser
from ..services.teams_service import update_team, delete_team, isUser, isLeader , isViceLeader ,  deleteUserFromGroup , createNewTeamCode


team_bp = Blueprint('team' , __name__)
team_api = Api(team_bp)

class Teams(Resource):
    @jwt_required()
    def get(self, id = None):
        if id is None:
            logger.warning("Team GET request without team ID.")
            return {
                "success": False,
                "message": "Don't know team to get information"
            } , 400
            
        userID = int(get_jwt_identity())
        chk = isUser(userID)
        if not chk:
            logger.warning(f"User (id:{userID}) not found when trying to get team (id:{id}).")
            return {
                "success": False,
                "message": "User not found",
            } , 400
            
        chk = isUserMember(userID , id)
        if not chk:
            logger.warning(f"User (id:{userID}) attempted to access team (id:{id}) but is not a member.")
            return {
                "success": False, 
                "message": "User is not a member of this team" 
            } , 400
            
        response_data = getTeamByID(id , userID=userID)
        logger.info(f"User (id:{userID}) retrieved team (id:{id}) information.")
        return response_data
        
    @jwt_required() 
    def post(self):
        current_user_id = int(get_jwt_identity()) 
        if not(current_user_id): 
            logger.warning("Team creation failed: Can't read information from token.")
            return {
                "success": False,
                "message": "Can't read information from token"
            }, 401
            
        if not(isUser(current_user_id)):
            logger.warning(f"Team creation failed: User (id:{current_user_id}) not found.")
            return {
                "success": False,
                "message": "User not found"
            } , 401

        data = dict(create_new_team_parser.parse_args())
        name = data.get('teamName')
        icon = data.get('icon')
        banner = data.get('banner')
        description = data.get('description')

        new_team = Team()
        new_team.name = name
        new_team.description = (description if description else '')
        new_team.leader_id = current_user_id
        new_team.leader = db.session.query(User).filter(User.id == current_user_id).first()
        new_team.banner_url = None
        new_team.icon_url = None
        
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

        code = createCodeForTeam(new_team.id , 604800)

        stmt = team_member_association.insert().values(
                team_id = new_team.id,
                user_id = current_user_id
            )
        db.session.execute(stmt)
        db.session.commit()
        
        logger.info(f"User (id:{current_user_id}) created new team (id:{new_team.id}, name:{name}).")
        return {
            "success": True,
            "message": "Your team has been completed successfully. You can join with the code below",
            "data": queryTeam(new_team.id),
            "code": code
        } , 201
        
    @jwt_required()
    def put(self, id = None):
        userID = int(get_jwt_identity())
        if not userID:
            logger.warning("Team update failed: Token is invalid.")
            return {
                "success": False,
                "message": "Your token is failed to make any updated"
            } , 401
            
        if not isUser(userID):
            logger.warning(f"Team update failed: User (id:{userID}) not found.")
            return {
                "success": False,
                "message": "User not found"
            } , 401
            
        team = db.session.query(Team.leader_id , Team.vice_leader_id).filter(Team.id == id).first()
        if not team:
            logger.warning(f"Team update failed: Team (id:{id}) not found.")
            return {
                "success": False,
                "message": "Don't know team to update"
            } , 401
            
        if userID == int(team[0]) or (team[1] and userID == int(team[1])):
            data = update_team_parser.parse_args()
            response_data = update_team(userID , id , data)
            logger.info(f"User (id:{userID}) updated team (id:{id}).")
            return response_data
        else:
            logger.warning(f"User (id:{userID}) attempted to update team (id:{id}) without permission.")
            return {
                "success": False,
                "message": "You don't have any permission to do this action"
            } , 403

    @jwt_required()
    def delete(self , id):
        current_user_id = int(get_jwt_identity())
        information = db.session.query(Team.leader_id).filter(id == Team.id).first()

        if not information:
            logger.warning(f"Team deletion failed: Team (id:{id}) not found.")
            return {
                "success": False,
                "message": "Team not found to delete"
            } , 400
            
        if int(information[0]) != current_user_id:
            logger.warning(f"User (id:{current_user_id}) attempted to delete team (id:{id}) without permission.")
            return {
                "success": False,
                "message": "You dont have permission to do this action"
            } , 403

        response_data = delete_team(id)
        logger.info(f"User (id:{current_user_id}) deleted team (id:{id}).")
        return response_data , 200

class TeamJoinCode(Resource):
    def post(self, id):
        time = request.json.get('expiresIn')
        if time is None:
            logger.warning(f"Team code creation failed for team (id:{id}): Missing expiration time.")
            return {
                "Success": False,
                "message": "Missing time to create team code"
            } , 400
            
        if id is None:
            logger.warning("Team code creation failed: Team ID not provided.")
            return {
                "Success": False,
                "Message": "Team not found"
            } , 400
            
        code = createCodeForTeam(id , int(time))
        if code is None:
            logger.warning(f"Team code creation failed for team (id:{id}): Missing information.")
            return {
                "Success": False,
                "message": "Missing information to create team code"
            } , 401
            
        logger.info(f"Team code created for team (id:{id}) with expiration time {time}s.")
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
            logger.warning("Team code retrieval failed: Invalid user token.")
            return {
                "success": False, 
                "message": "Code is invalid"
            } , 401
            
        team_id = team_code_parser.parse_args().get('teamID') 
        chk = isUserMember(userID=current_user_id , teamID=team_id) 
        if not chk:
            logger.warning(f"User (id:{current_user_id}) attempted to get code for team (id:{team_id}) but is not a member.")
            return {
                "success": False, 
                "message": "You don't belong to this team"
            }, 401
            
        code = getTeamCode(team_id)
        logger.info(f"User (id:{current_user_id}) retrieved team code for team (id:{team_id}).")
        return {
            "success": True, 
            "code": code 
        }
        
    @jwt_required() 
    def post(self): 
        current_user_id = int(get_jwt_identity()) 
        if current_user_id is None:
            logger.warning("New team code creation failed: Invalid user token.")
            return {
                "success": False, 
                "message": "Code is invalid"
            } , 401
            
        data = dict(create_new_team_code_parser.parse_args())
        team_id = data.get('teamID')
        
        is_lead = isLeader(user_id=current_user_id , team_id=team_id) 
        is_vice_lead = isViceLeader(user_id=current_user_id , team_id = team_id) 
        
        if is_lead or is_vice_lead: 
            code = createNewTeamCode(team_id)
            logger.info(f"User (id:{current_user_id}) created new team code for team (id:{team_id}).")
            return {
                "success": True, 
                "message": "This is the new code for your team", 
                "code": code 
            }
            
        logger.warning(f"User (id:{current_user_id}) attempted to create new code for team (id:{team_id}) without permission.")
        return {
            "success": False, 
            "message": "You don't have enough permission", 
        } , 403 

class TeamJoin(Resource):
    @jwt_required()
    def post(self):
        current_user_id = int(get_jwt_identity())
        if not current_user_id:
            logger.warning("Team join failed: User not identified.")
            return {
                "success": False,
                "message": "User not identity"
            } , 401

        data = request.json
        code = data.get('code')

        teamID = db.session.query(InviteCode.team_id).filter(code == InviteCode.code).first()

        if not teamID:
            logger.warning(f"User (id:{current_user_id}) attempted to join team with invalid or expired code.")
            return {
                "success": False,
                "message": "Your code has been expired or incorrect"
            } , 401
            
        teamID = int(teamID[0])

        chk = isUserMember(current_user_id , teamID)
        if chk:
            logger.warning(f"User (id:{current_user_id}) attempted to join team (id:{teamID}) but is already a member.")
            return {
                "success": False,
                "message": "You has been a member of this team"
            }

        addMemberToTeam(current_user_id , teamID)
        logger.info(f"User (id:{current_user_id}) joined team (id:{teamID}).")
        return {
            "sucess": True,
            "message": "You have been joined successfully"
        } ,200

class UserWithTeam(Resource):
    @jwt_required()
    def get(self):
        current_user_id = int(get_jwt_identity())
        if not current_user_id:
            logger.warning("Get user teams failed: User not found.")
            return {
                "success": False,
                "message": "User not found to get all teams"
            } , 401
            
        if not isUser(current_user_id):
            logger.warning(f"Get user teams failed: User (id:{current_user_id}) not found.")
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
        logger.info(f"User (id:{current_user_id}) retrieved all their teams.")
        return {
            "success": True,
            "message": "This is all teams you joined",
            "teamData": teams
        } , 200
        
    @jwt_required()
    def delete(self):
        current_user_id = int(get_jwt_identity())
        teamID = user_leave_parser.parse_args().get('teamID')
        
        if not isUserMember(current_user_id , teamID):
            logger.warning(f"User (id:{current_user_id}) attempted to leave team (id:{teamID}) but is not a member.")
            return {
                "success": False,
                "message": "You don't belong to this group"
            } , 400
            
        if isLeader(current_user_id , teamID):
            logger.warning(f"Leader (id:{current_user_id}) attempted to leave team (id:{teamID}).")
            return {
                "success": False,
                "message": "Leader cannot leave the group"
            } , 403
            
        deleteUserFromGroup(current_user_id , teamID)
        logger.info(f"User (id:{current_user_id}) left team (id:{teamID}).")
        return {
            "success": True,
            "message": "You have leaved group successfully"
        } , 200

class TeamRole(Resource): 
    @jwt_required() 
    def get(self): 
        current_user_id = int(get_jwt_identity()) 
        if not current_user_id:
            logger.warning("Get team role failed: Invalid token or user ID.")
            return {
                "success": False, 
                "message": "Invalid token or id" 
            } , 200
            
        data = user_role_parser.parse_args() 
        teamID = data.get('teamID') 
        if not teamID:
            logger.warning(f"Get team role failed for user (id:{current_user_id}): Team not found.")
            return {
                "success": False, 
                "message": "Team not found"
            } , 200
            
        chk = isUserMember(current_user_id , teamID) 
        if not chk:
            logger.warning(f"User (id:{current_user_id}) attempted to get role for team (id:{teamID}) but is not a member.")
            return {
                "success": False, 
                "message": "You dont belong to this team"
            } , 200
            
        leader_id = db.session.query(Team.leader_id).filter(teamID == Team.id).first() 
        vice_leader_id = db.session.query(Team.vice_leader_id).filter(teamID == Team.id).first() 
        
        role = "member"
        if leader_id[0] == current_user_id:
            role = "leader"
        elif vice_leader_id[0] == current_user_id:
            role = "vice"
            
        logger.info(f"User (id:{current_user_id}) retrieved their role ({role}) for team (id:{teamID}).")
        return {
            "success": True, 
            "role": role 
        }

class LeaderKickUser(Resource):
    @jwt_required()
    def delete(self):
        current_user_id = int(get_jwt_identity())
        if not isLeader(current_user_id):
            logger.warning(f"User (id:{current_user_id}) attempted to kick member without leader permission.")
            return {
                "success": False,
                "message": "You don't have permission to do this action"
            }
            
        data = leader_kick_parser.parse_args()
        teamID = data.get('teamID')
        userID = data.get('userID')
        
        if not(teamID) or not(userID):
            logger.warning(f"Leader (id:{current_user_id}) attempted to kick user with missing information.")
            return {
                "success": False ,
                "message": "Missing information to delete"
            } , 401
            
        if not(isUserMember(userID , teamID)):
            logger.warning(f"Leader (id:{current_user_id}) attempted to kick user (id:{userID}) from team (id:{teamID}) but user is not a member.")
            return {
                "success": False,
                "message": "This user don't belong to your group"
            } , 400
            
        deleteUserFromGroup(userID , teamID)
        logger.info(f"Leader (id:{current_user_id}) kicked user (id:{userID}) from team (id:{teamID}).")
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