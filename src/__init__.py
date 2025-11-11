from flask import Flask 
from .config.dev_config import DevConfig
from dotenv import load_dotenv 

load_dotenv() 
app = Flask(__name__)
dev_config = DevConfig() 
