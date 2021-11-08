from flask import Flask
from .sms import sms
from .extensions import db
from .config import config
import pymysql
from .extensions import jwt, admin, migrate, db



pymysql.install_as_MySQLdb()




def create_app(config_name):
    app = Flask(__name__)
    
    #initialize the data with the app
    db.init_app(app)
    jwt.init_app(app)
    admin.init_app(app)
    

    #the configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    migrate.init_app(app, db)

    
    app.register_blueprint(sms, url_prefix='/sms')
    
    


    return app
