import os 
from src import create_app
from src.config.dev_config import DevConfig
from flask_cors import CORS, cross_origin


app = create_app()
dev_config = DevConfig()
CORS(app , supports_credentials=True) 
url = 'http://localhost:' + str(dev_config.PORT) 


@app.route('/my-testing') 
def index():
    return {
        "success": True , 
        "message": "Testing thanh cong"
    }

if __name__ == '__main__': 
    print('Server khoi dong thanh cong tai: ' , url)
    app.run(port=dev_config.PORT , debug=dev_config.DEBUG)