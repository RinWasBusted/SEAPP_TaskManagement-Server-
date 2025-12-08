import datetime
from ..models import db 
from ..models.team_model import Team 
from ..models.user_model import User 
from ..models.task_model import Task 
from sqlalchemy.orm import aliased 
from ..models.association import team_member_association, assignment_association
from sqlalchemy import select, insert
from ..controllers.parsers import create_new_team_parser
from ..models.invite_code_model import InviteCode 
from .randomCode import randomCode 
from .datetime_service import addTime, toStr, getNow
from ..utils import getImageUrl
import cloudinary.uploader 


# Viet lai team service 
# Ham kiem tra the loai member 
def isMember(user_id, team_id):
    stmt = select(team_member_association).where(team_member_association.c.user_id == user_id, team_member_association.c.team_id == team_id)
    
    result = db.session.execute(stmt).first

    if(result): return True
    return False

def isViceLeader(user_id, team_id):
    chk = db.session.query(1).filter(Team.id == team_id).filter(Team.vice_leader_id == user_id).first() 
    
    if chk: return True 
    return False 

def isLeader(user_id, team_id):
    chk = db.session.query(1).filter(Team.id == team_id).filter(Team.leader_id == user_id).first() 
    # leader_id = db.session.query(Team.leader_id).filter(Team.id == team_id).filter(Team.leader_id == user_id).first() 
    if chk: return True 
    return False 

def getRole(userID , teamID): 
    if isViceLeader(userID , teamID) == True: 
        return "vice-leader" 
    if isLeader(userID , teamID) == True: 
        return "leader" 
    return "member" 

# Kiem tra co phai user hay khong 
def isUser(id): 
    user_id = db.session.query(1).filter(id == User.id).first() 
    if user_id: return True 
    return False 

def isTeam(id): 
    team = db.session.query(1).filter(id == Team.id).first() 
    if team: return True 
    return False 

def createCode(): 
    code = randomCode(8) 
    exists = db.session.query(1).filter(InviteCode.code == code).first() 
    if exists: 
        code = randomCode(9) 
    return code 

def isUserMember(userID , teamID): 
    # Kiem tra userID nay co phai la thanh vien cua teamID hay khong 
    stmt = select(1).where(
        team_member_association.c.user_id == userID, 
        team_member_association.c.team_id == teamID 
    ) 
    e = db.session.execute(stmt).first() 
    if e: 
        return True 
    return False 

def addMemberToTeam(userID , teamID): 
    stmt = insert(team_member_association).values(
        user_id = userID, 
        team_id = teamID 
    )
    db.session.execute(stmt) 
    db.session.commit() 


def createCodeForTeam(teamID , expise): # Ham dung de tao code cho team 
    
    if not isTeam(teamID): return None # Neu khong co team thi se khong tao group 
    
    code = createCode() 
    new_invite_code = InviteCode()  
    new_invite_code.code = code 
    new_invite_code.time_expired = addTime(datetime=datetime.datetime.now() , second= expise) 
    new_invite_code.team_id = teamID #Bat buoc phai gan lai cai nay 
    invite = db.session.query(InviteCode).filter(InviteCode.team_id == teamID).first() 
    
    if invite: 
        invite.code = code 
        invite.time_expired = addTime(datetime=datetime.datetime.now() , second= expise) 
    else: 
        db.session.add(new_invite_code) 
    db.session.commit() 
    return code 
    

def queryTeam(id): 
    team = db.session.query(Team.id , Team.name , Team.icon_url , Team.banner_url , Team.leader_id , Team.vice_leader_id , Team.description).filter(id == Team.id).first() 
    if team: 
        return {
            "teamID": team[0], 
            "teamName": team[1], 
            "icon": getImageUrl(team[2]), 
            "banner": getImageUrl(team[3]), 
            "leaderID": team[4], 
            "viceLeaderID": team[5], 
            "description": team[6] 
        }
    return None # Khong tim thay team 

# Upload anh len cloudinary danh rieng cho teams 
def uploadTeamImage(team , file = '' , type = 'icon'): 
    if (file and team): 
        if type == 'icon': 
            if team.icon_url: 
                cloudinary.uploader.destroy(team.icon_url) 
            upload_result = cloudinary.uploader.upload(file) 
            team.icon_url = upload_result['public_id'] 
            return upload_result['secure_url']
        else: 
            if team.banner_url:
                cloudinary.uploader.destroy(team.banner_url) 
            upload_result = cloudinary.uploader.upload(file) 
            team.banner_url = upload_result['public_id']
            return upload_result['secure_url']
#Lay thong tin cua team theo id 
def getTeamByID(id , userID): 
    Leader = aliased(User) 
    ViceLeader = aliased(User) 
    
    exists = db.session.query(
        Team.id , Team.name , Team.icon_url , Team.banner_url , Team.description,
        Leader, 
        ViceLeader 
        ).join(Leader , Leader.id == Team.leader_id).outerjoin(ViceLeader , ViceLeader.id == Team.vice_leader_id).filter(Team.id == id).first() 
    
    if not exists: 
        return {
            "success": False, 
            "message": "Team not found"
        } , 401 
    role = "member" 
    leader = exists[5].to_dict() 
    if userID == leader['id']: 
        role = "leader"
    vice_leader = None 
    if exists[6]: 
        vice_leader = exists[6].to_dict() 
        if userID == vice_leader['id']: 
            role = "vice_leader"
    code = db.session.query(InviteCode.code).filter(InviteCode.team_id == id).first() 
    team = {
        "id": exists[0], 
        "name": exists[1], 
        "icon": getImageUrl(str(exists[2])),
        "banner": getImageUrl(str(exists[3])),
        "description": str(exists[4]), 
        "code": code[0], 
        
    } 

    users = db.session.query(User).join(team_member_association , team_member_association.c.user_id == User.id).filter(team_member_association.c.team_id == id).all() 
    users = [
        {
        **user.to_dict(),
        "role": "leader" if user.id == leader.get('id')
                else ("vice-leader" if vice_leader and user.id == vice_leader.get('id') else "member")
        }
        for user in users
    ]
    
    response_data = {
        "success": True, 
        "message": "This is the information about the team you need", 
        "teamData": team, 
        "leader": leader, 
        "viceLeader": vice_leader, 
        "members": users, 
        "role": role 
    } , 200 
    
    return response_data 
      
# [POST] 

                
def update_team(userID, id, data):  # id = teamID
    data = dict(data)

    icon = data.get('icon')
    banner = data.get('banner')
    name = data.get('teamName')
    description = data.get('teamDescription')
    leaderID = data.get('leaderID')
    viceLeaderID = data.get('viceLeaderID')

    response_data = {
        "teamID": id
    }

    # Lấy team
    team = db.session.query(Team).filter(Team.id == id).first()
    if not team:
        return {
            "success": False,
            "message": "Team not found",
            "data": {}
        }, 404

    currentLeader = team.leader_id
    currentViceLeader = team.vice_leader_id

    # --- Update name ---
    if name:
        team.name = name
        response_data['teamName'] = name

    # --- Update icon ---
    if icon:
        iconUrl = uploadTeamImage(team, icon, 'icon')
        response_data['iconUrl'] = iconUrl

    # --- Update banner ---
    if banner:
        bannerUrl = uploadTeamImage(team, banner, 'banner')
        response_data['bannerUrl'] = bannerUrl

    # --- Update description ---
    if description:
        team.description = description
        response_data['description'] = description

    # --- Update Leader ---
    if leaderID is not None:
        if not isMember(leaderID, id):
            response_data['leaderID'] = 'This person is not the member of this team'
        elif currentLeader != userID:
            response_data['leaderID'] = "You don't have permission to do this"
        elif leaderID == currentLeader:
            response_data['leaderID'] = "This person is already the leader"
        else:
            # Xóa quyền Vice-Leader nếu người này đang là Vice-Leader
            if team.vice_leader_id == leaderID:
                team.vice_leader = None
                team.vice_leader_id = None
                response_data['viceLeaderID'] = None  # báo frontend quyền bị xóa
            # Chỉ định Leader mới
            newLeader = db.session.query(User).filter(User.id == leaderID).first()
            if newLeader:
                team.leader = newLeader
                team.leader_id = leaderID
                response_data['leaderID'] = leaderID
            else:
                response_data['leaderID'] = "Error in find leader"

    # --- Update Vice-Leader ---
    if viceLeaderID is not None:
        if not isMember(viceLeaderID, id):
            response_data['viceLeaderID'] = 'This person is not the member of this team'
        else:
            # Quyền update vice-leader
            if currentLeader == userID:
                # Leader có quyền update vice-leader
                if viceLeaderID == currentLeader:
                    response_data['viceLeaderID'] = "Cannot assign leader as vice-leader"
                else:
                    newVice = db.session.query(User).filter(User.id == viceLeaderID).first()
                    if newVice:
                        team.vice_leader = newVice
                        team.vice_leader_id = viceLeaderID
                        response_data['viceLeaderID'] = viceLeaderID
                    else:
                        response_data['viceLeaderID'] = "Error in find vice leader"
            elif currentViceLeader == userID:
                # Vice-leader chỉ được đổi vice-leader, không đổi leader
                if viceLeaderID == currentLeader:
                    response_data['viceLeaderID'] = "Cannot assign leader as vice-leader"
                elif viceLeaderID == currentViceLeader:
                    response_data['viceLeaderID'] = "This person is already the vice-leader"
                else:
                    newVice = db.session.query(User).filter(User.id == viceLeaderID).first()
                    if newVice:
                        team.vice_leader = newVice
                        team.vice_leader_id = viceLeaderID
                        response_data['viceLeaderID'] = viceLeaderID
                    else:
                        response_data['viceLeaderID'] = "Error in find vice leader"
            else:
                response_data['viceLeaderID'] = "You don't have permission to do this"

    # --- Commit database ---
    db.session.commit()

    return {
        "success": True,
        "message": "Your team has been updated successfully",
        "data": response_data
    }


def dropImage(id): 
    cloudinary.uploader.destroy(id)   
      
def delete_team(id): 
    team = db.session.query(Team).filter(id == Team.id).first() 
    tasks = db.session.query(Task).filter(Task.team_id == id).all() 
    
    db.session.execute(
        assignment_association.delete().where(assignment_association.c.task_id.in_([t.id for t in tasks]))
    )

    db.session.execute(
        team_member_association.delete().where(team_member_association.c.team_id == id)
    )
    
    for x in tasks: 
        db.session.delete(x) 
    inviteCode = db.session.query(InviteCode).filter(InviteCode.team_id == id).first() 
    db.session.delete(inviteCode) 
    db.session.delete(team) 
    db.session.commit() 
    return {
        "success": True, 
        "message": "Your team has been deleted successfully"
    }

    
def join_code(code , userID): 
    qr = db.session.query(InviteCode).filter(InviteCode.code == code).first() 
    if qr: 
        team_id = qr.team_id 
        team = db.session.query(Team).filter(Team.id == team_id).first() 
        user = db.session.query(User).filter(User.id == userID).first() 
        if team and user: 
            exists_stmt = select(team_member_association).where(
                team_member_association.c.user_id == user.id,
                team_member_association.c.team_id == team_id
            )

            row = db.session.execute(exists_stmt).first()

            if row:
                return {
                    "success": False,
                    "message": "User already joined this team"
            }
            stmt = team_member_association.insert().values(
                team_id = team_id, 
                user_id = user.id 
            )
            db.session.execute(stmt) 
            db.session.commit() 
            response_data = {
                "success": True, 
                "message": "Join team successfully", 
                "data": {
                    "teamID": team_id, 
                    "joinAt": toStr(getNow()), 
                    "teamName": team.name 
                }
            }
            return response_data 
        else: return {
            "success": False, 
            "message": "Cannot find the team with this code"
        }
    return {
        "success": False, 
        "message": "The code is invalid"
    }
    
def deleteUserFromGroup(userID , teamID): 
    team = db.session.query(Team).filter(teamID == Team.id).first() 
    if team and isViceLeader(userID , teamID): 
        team.vice_leader_id = None   #foreign key 
        team.vice_leader = None  #relationship 
    # Tien hanh xoa cap user_id , team_id nay trong db.Column 
    stmt = team_member_association.delete().where(
        (team_member_association.c.user_id == userID) & 
        (team_member_association.c.team_id == teamID) 
    )
    # Thuc hien xoa nhung cai duoc giao cho userID bi xoa 
    tasks = db.session.query(Task.id).filter(Task.team_id == teamID).all() 
    stmp = assignment_association.delete().where(
        (assignment_association.c.task_id.in_([t[0] for t in tasks])) & 
        (assignment_association.c.user_id == userID)
    )
    
    for x in tasks: 
        db.session.delete(x) 
    
    
    db.session.execute(stmt) # Thuc hien cau lenh 1 
    db.session.execute(stmp) # Thuc hien cau lenh 2 
    db.session.commit() 
    return True 

def getTeamCode(teamID): 
    code = db.session.query(InviteCode.code).filter(InviteCode.team_id == teamID).first() 
    return code[0] 

def createNewTeamCode(teamID): 
    code = createCode() 
    time_expred = addTime(datetime=datetime.datetime.now() , second=604800) 
    team_code = db.session.query(InviteCode).filter(InviteCode.team_id == teamID).first() 
    team_code.code = code 
    team_code.time_expired = time_expred
    db.session.commit() 
    return code 