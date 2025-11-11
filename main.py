from src import app, dev_config
from src.api import api_bp
url = 'http://localhost:' + str(dev_config.PORT) 
if __name__ == '__main__': 
    print('Server khoi dong thanh cong tai: ' , url)
    app.register_blueprint(api_bp) 
    app.run(port=dev_config.PORT , debug=dev_config.DEBUG)