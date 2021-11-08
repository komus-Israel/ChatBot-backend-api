from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.ext.automap import automap_base
from flask_jwt_extended import JWTManager
from flask_admin import Admin
from flask_admin.contrib.fileadmin import FileAdmin
from flask_migrate import Migrate



db = SQLAlchemy()
jwt = JWTManager()
admin = Admin(name=None, template_mode='bootstrap4')
migrate = Migrate()

class FileAdmin(FileAdmin):
    can_upload = False
    can_delete_dirs = False 
    can_rename = False 
    can_mkdir = False 
    can_create = False 
    can_delete = False 




  



