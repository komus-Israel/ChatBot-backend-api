from .extensions import db
from passlib.apps import custom_app_context as pwd_context
#from flask_admin.contrib.sqla import ModelView
from datetime import date
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import os
from flask_admin.contrib.sqla import ModelView



class Student(db.Model):

    id = db.Column(db.Integer, primary_key =True)
    student_id = db.Column(db.String(200), index =True, nullable=False)
    date_registered = db.Column(db.String(200), nullable=False, default=date.today)
    first_name = db.Column(db.String(200), index =True)
    last_name = db.Column(db.String(200), index =True)
    level = db.Column(db.String(200), index =True)
    password_hash = db.Column(db.String(200), nullable = False)
    student = db.relationship('FeedBack', backref = 'student')
    student_chat = db.relationship('ChatLog', backref = 'student')
     
     

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


    
    

class Admin(db.Model):

    id = db.Column(db.Integer, primary_key =True)
    admin_id = db.Column(db.String(200), index =True, nullable=False)
    date_registered = db.Column(db.String(200), nullable=False, default=date.today)
    first_name = db.Column(db.String(200), index =True)
    last_name = db.Column(db.String(200), index =True)
    password_hash = db.Column(db.String(200), nullable = False)
    

    

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)
    
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class FeedBack(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    feedback = db.Column(db.Text, index =True, nullable=False)
    date = db.Column(db.String(200), nullable=False, default=date.today)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    read = db.Column(db.Boolean, default=False)

class CustomModelView(ModelView):

    can_export = True
    can_delete = True 


class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    date = db.Column(db.String(200), nullable=False, default=date.today)
    student_msg = db.Column(db.Text)
    bot_msg = db.Column(db.Text)
    student_time = db.Column(db.String(200))
    bot_response_time = db.Column(db.String(200))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))



