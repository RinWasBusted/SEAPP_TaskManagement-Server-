from ..models import db
from ..models.user_model import User

def getUserFromId(userId : int):
    user = db.session.get(User, userId)
    return user.to_dict()