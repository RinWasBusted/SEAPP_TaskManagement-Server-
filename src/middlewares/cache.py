from src.extensions import app_cache
import ast
import inspect
from functools import wraps


def data_caching(key: str, ttl:int, tags:list = []):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Lấy tên các tham số trong args
            sig = inspect.signature(fn)
            # Gán giá trị vào các tham số tương ứng
            bound_args = sig.bind(*args, **kwargs)
            # Chuyển thành dạng dict để dùng
            arg_dict = bound_args.arguments

            try:
                cache_key = key.format(**arg_dict)
            except KeyError as e:
                raise ValueError(f"The {e} parameter is not exists!")

            cached_data = app_cache.get(cache_key)

            if(cached_data):
                return ast.literal_eval(cached_data)
            
            result = fn(*args, **kwargs)

            app_cache.set(cache_key, str(result), ex=ttl)

            return result
        
        return wrapper
    return decorator
