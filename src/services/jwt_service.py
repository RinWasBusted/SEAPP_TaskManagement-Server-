from flask_jwt_extended import decode_token
from flask import current_app
from google.oauth2 import id_token
from google.auth.transport import requests

def decode_google_token(token: str):
    try:
        # Verify token với Google
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), audience=None, clock_skew_in_seconds=60)
        # Nếu cần, bạn có thể check aud (client_id) để đảm bảo token là của app bạn
        if not idinfo.get("email_verified"):
            return None

        return {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "user_id": idinfo.get("sub")  # Google unique user id
        }
    except ValueError as e:
        # Token không hợp lệ hoặc expired
        print(f"Lỗi decode Google token: {e}")
        return None

def decode_verification_token(token):
    try:
        payload = decode_token(token)
        email = payload.get('email') 
        password_hash = payload.get('password_hash')
        purpose = payload.get('purpose')

        if purpose != 'email_verification':
            return None

        return {
            'email': email,
            'password_hash': password_hash,
            'name': payload.get('name') 
        }
    except Exception as e:
        print(f"Lỗi giải mã token: {e}")
        return None       


def decode_reset_password_token(token: str):
    try:
        payload = decode_token(token)
        purpose = payload.get('purpose')

        if purpose != 'reset_password':
            return None

        user_id = payload.get('user_id')
        return {
            'user_id': user_id
        }
    except Exception as e:
        print(f"Lỗi giải mã token: {e}")
        return None       