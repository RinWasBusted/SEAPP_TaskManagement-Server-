from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from services.team_service import isMember, isViceLeader, isLeader

def require_login_method(method):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('login_method') != method:
                return {
                    "success": False,
                    "message": f"This action requires {method} login"
                }, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role:str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            team_id = kwargs.get('team_id')

            if(isLeader(user_id=user_id, team_id=team_id)): return fn(*args, **kwargs)

            if(isViceLeader(user_id=user_id, team_id=team_id) and role in ['member','viceleader']): return fn(*args, **kwargs)

            if(isMember(user_id=user_id, team_id=team_id) and role == 'member'): return fn(*args, **kwargs)

            return {
                "success": False,
                "message": "You are not the leader of this team"
            }, 403

        return wrapper

    return decorator

