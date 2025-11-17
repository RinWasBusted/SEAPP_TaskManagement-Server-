from src import create_app
from src.config.dev_config import DevConfig

app = create_app()
dev_config = DevConfig()

url = 'http://localhost:' + str(dev_config.PORT) 

if __name__ == '__main__': 
    print('Server khoi dong thanh cong tai: ' , url)
    app.run(port=dev_config.PORT , debug=dev_config.DEBUG)