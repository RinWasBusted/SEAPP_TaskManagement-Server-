from src import create_app 
from src.config.dev_config import DevConfig

app = create_app() 
dev = DevConfig() 
if __name__ == '__main__': 
    print('Server khoi dong thanh cong') 
    app.run(port=dev.PORT , debug=dev.DEBUG) 