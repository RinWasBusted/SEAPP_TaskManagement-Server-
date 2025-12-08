from redis import Redis
from dotenv import load_dotenv
import os
import logging.config
import pathlib
import json

load_dotenv()

app_cache = Redis(host='localhost', port=6379, password=os.getenv('REDIS_PASSWORD'), decode_responses=True, db=0)

jwt_blacklist = Redis(host='localhost', port=6379, password=os.getenv('REDIS_PASSWORD'), decode_responses=True, db=0) 

logger = logging.getLogger('my_app')
config_file = pathlib.Path("src/config/logging_config.json")
with open(config_file) as f_in:
    config = json.load(f_in)
logging.config.dictConfig(config=config)