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