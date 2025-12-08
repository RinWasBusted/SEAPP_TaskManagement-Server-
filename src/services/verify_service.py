import os 
from google.oauth2 import id_token 
from google.auth.transport import requests
def verfyGoogleToken(token): 
    try:
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            os.environ.get('OAUTH_CLIENT_CLIENT_ID_2')
        )
        if not idinfo.get('email_verified'):
            return False 
        return True 
    except ValueError as e: 
        return False 