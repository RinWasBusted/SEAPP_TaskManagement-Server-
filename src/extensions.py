from redis import Redis
from dotenv import load_dotenv
import os

load_dotenv()

app_cache = Redis(host='localhost', port=6379, password=os.getenv('REDIS_PASSWORD'), decode_responses=True, db=0)

jwt_blacklist = Redis(host='localhost', port=6379, password=os.getenv('REDIS_PASSWORD'), decode_responses=True, db=0) 


