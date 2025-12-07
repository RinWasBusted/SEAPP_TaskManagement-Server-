from cloudinary.utils import cloudinary_url
from src.extensions import app_cache

def getImageUrl(public_id):
    result_tuple = cloudinary_url(public_id, secure=True)
    return result_tuple[0]

# def cacheData(key:str, data:dict, ttl:int):
#     try:
#         value = str(data)
#         return app_cache.set(key=key, value=value, ex=ttl)
#     except Exception as e:
#         return None

def invalidateCache(*args):
    try:
        for key in args:
            app_cache.delete(key)
    except Exception as e:
        return None