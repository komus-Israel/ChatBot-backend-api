from .extensions import db
from passlib.apps import custom_app_context as pwd_context
#from flask_admin.contrib.sqla import ModelView
from datetime import date
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import os



class Student(db.Model):

    #__tablename__ = 'Customer'

    id = db.Column(db.Integer, primary_key =True)
    student_id = db.Column(db.String(200), index =True, nullable=False)
    date_registered = db.Column(db.String(200), nullable=False, default=date.today)
    first_name = db.Column(db.String(200), index =True)
    last_name = db.Column(db.String(200), index =True)
    level = db.Column(db.String(200), index =True)
    password_hash = db.Column(db.String(200), nullable = False)
    

    

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    '''def get_reset_token(self, expires_sec=1800):
        s = Serializer('213efdsvfgtre435trgfbnhmjhgtr56y7ujmnbvdsvdf', expires_sec)
        return s.dumps({'customer_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer('213efdsvfgtre435trgfbnhmjhgtr56y7ujmnbvdsvdf')
        try:
            _id = s.loads(token)['customer_id']
        except:
            return None 
        return Customer.query.get(_id)'''

    
    

class Admin(db.Model):

    #__tablename__ = 'Customer'

    id = db.Column(db.Integer, primary_key =True)
    email = db.Column(db.String(200), index =True, nullable=False)
    date_registered = db.Column(db.String(200), nullable=False, default=date.today)
    first_name = db.Column(db.String(200), index =True)
    last_name = db.Column(db.String(200), index =True)
    password_hash = db.Column(db.String(200), nullable = False)
    

    

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

