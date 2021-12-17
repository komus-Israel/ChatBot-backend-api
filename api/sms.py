from flask import Blueprint, jsonify, request, make_response, g, send_from_directory
from flask_jwt_extended.utils import get_current_user
from keras.utils.io_utils import path_to_string
from nltk import probability
from tensorflow.python.eager.context import context
from .extensions import db
from .models import FeedBack, Student, Admin, CustomModelView, ChatLog
import json
from datetime import datetime
from datetime import date
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from .extensions import jwt, admin
from flask_cors import CORS, cross_origin
from collections import Counter
from .view_functions import (
                            search_engine, serialize_student, predict_class,
                            getResponse, serialize_feedback, getTime, log_serializer
                            )
from .model.train import train_bot
from keras.models import load_model
import os



#   initialize the blueprint for the API version1

sms = Blueprint('sms', __name__)
CORS(sms, resources={r"/sms/*": {"origins":"*"}})
intents = json.loads(open("./api/model/chatbot.json").read())

tags = [intent['tag'] for intent in intents['intents']]



'''
    Add admin views
'''

admin.add_view(CustomModelView(Student, db.session))
admin.add_view(CustomModelView(FeedBack, db.session))
admin.add_view(CustomModelView(ChatLog, db.session))




#   routes for the API endpoints


#   This route is defined to help us know if our application is well runing. It is the route to the index page of the API's version1

@sms.route('/')
def index():
    return 'Working well'
    


@sms.route('/student/register',methods = ['POST'])
def register_student():
    
    if request.method == 'POST':

        try:
            first_name = request.json['first_name']
            last_name = request.json['last_name']
            level = request.json['level']
            matric_no = request.json['matric_no']
        except Exception as KeyError:
            error = KeyError.args
            return jsonify(status='failed', msg = f'{error[0]} field is missing in your request'), 400

        check_student_from_student = Student.query.filter_by(student_id=matric_no).first()
        check_student_from_admin = Admin.query.filter_by(admin_id=matric_no).first()

        if check_student_from_admin or check_student_from_student:
            return jsonify(status='failed', msg='This matric has been registered')

        student = Student(
            
            first_name = first_name,
            last_name = last_name,
            student_id = matric_no,
            level = level
        )
        
        student.hash_password(matric_no)

        db.session.add(student)
        db.session.commit()

        return jsonify(status = 'success', msg = 'student registered successfully')



@sms.route('/student/total',methods = ['GET'])
def get_no():
    no_of_student = len(Student.query.all())
    return jsonify(status='success', no_of_student=no_of_student)


@sms.route('/student/delete',methods = ['GET'])
def delete_student():
    matric_no = request.args.get('matric_no')
    check_for_matric_no = Student.query.filter_by(student_id=matric_no).first()

    if not check_for_matric_no:
        return jsonify(status='failed', msg=f'No student with matric number {matric_no}')

    student_feedbacks = FeedBack.query.filter_by(student=check_for_matric_no).all()

    if len(student_feedbacks) == 0:
        pass 
    else:
        for feedbacks in student_feedbacks:
            db.session.delete(feedbacks)    

    db.session.delete(check_for_matric_no)
    db.session.commit()

    return jsonify(status='success', msg='student deleted successfully')


@sms.route('/student/search')
@cross_origin()
def search_student():
   
    search_param = request.args.get('search')
    search_query = Student.query
            
    search_result = [search_engine(search_query, i.lower()) for i in search_param.split(' ')] + [search_engine(search_query, i.upper()) for i in search_param.split(' ')] + [search_engine(search_query, i.capitalize()) for i in search_param.split(' ')]

    
    preprocessed_search_result = []

    try:
        for results_list in search_result:
            for result in results_list:
                preprocessed_search_result.append(result)
        preprocessed_search_result = Counter(preprocessed_search_result)
        search_result = list(preprocessed_search_result.keys())
    except Exception as e:
        pass
        
    
    serialized_result = [*map(serialize_student, search_result)]
    
    return jsonify(status='success', search_result= serialized_result)
    
@sms.route('/upload', methods = ['POST'])
@cross_origin()
def upload_content():
    
    file = request.files['file']
    file.save(f'./api/upload/{file.filename}')


    return jsonify(status='success', msg='uploaded successfully')


@sms.route('/train-bot', methods = ['POST'])
@cross_origin()
def train():

    tag = request.json['tag']
    patterns = request.json['patterns'].split(',')
    responses = request.json['responses'].split(',')

    if (tag == '' or  patterns == '' or responses == ''):
        return jsonify(status='failed', msg = "tag, patterns or responses can't be empty")

    new_intent = dict(tag=tag, patterns=patterns, responses=responses, context_set="")

    with open("./api/model/chatbot.json" , 'r') as bot_intent:
        intents = json.load(bot_intent)

    intents['intents'].append(new_intent)

    with open("./api/model/chatbot.json", 'w') as new_file:
	    json.dump(intents, new_file)
    
    train = train_bot()
   
    if train:
        return jsonify(status='success', msg = 'bot updated successfully')


@sms.route('/train-bot-with-no-update')
@cross_origin()
def train_bot_with_no_update():
    train = train_bot()
    if train:
        
        return jsonify(status='success', msg = 'bot updated successfully')


@sms.route('/chat')
@jwt_required()
@cross_origin()
def chat_bot():
     
    student_id = get_jwt_identity()
    student_id = Student.query.filter_by(student_id=student_id).first()


    message = request.args.get('message')
    student_time = getTime()

    

    if message[0] == ' ':
        message = message.replace(' ', '',1)
    
    bot_response_time = getTime()



    model = load_model("./api/model/chatbot_model.h5")

    predict_message = predict_class(message, model)

    bot_response = getResponse(predict_message, intents)

    bot_response_time = getTime()

    msg_log = ChatLog(
            student = student_id,
            bot_msg = bot_response['response'],
            student_msg = message,
            student_time = student_time,
            bot_response_time = bot_response_time
    )

    db.session.add(msg_log)
    db.session.commit()

 
    bot_response['status']= 'success'


    return bot_response
    

@sms.route('/login', methods=['POST'])
@cross_origin()
def login():
    if request.method == 'POST':
        try:
            _id = request.json['id']
            password = request.json['password']
        except Exception as KeyError:
            error = KeyError.args
            return jsonify(status='failed', message = f'{error[0]} field is missing in your login request'), 400
    

        student = Student.query.filter_by(student_id = _id).first()
        admin = Admin.query.filter_by(admin_id = _id).first()
    

        if not student or not student.verify_password(password):
            
            if not admin or not admin.verify_password(password):
                return jsonify(status = 'failed',msg = 'incorrect login details'), 403
            else:
                g.user = admin
                
                role = 'admin'

                access_token = create_access_token(identity = g.user.admin_id)
                
                return jsonify(access_token=access_token,status='success',msg= f'{g.user.admin_id} logged in successfully',
                role=role, id = g.user.admin_id)
        

        g.user = student
        role = 'student'
    
        access_token = create_access_token(identity = g.user.student_id)

        
        return jsonify(access_token=access_token, status = 'success',msg = f'{g.user.student_id} logged in successfully',
            role=role, id = g.user.student_id)
    



@sms.route('/admin/register')
@cross_origin()
def admin_register():
     if request.method == 'POST':
        try:       
            first_name = request.json['first_name']
            last_name = request.json['last_name']
            admin_id = request.json['admin_id']
            password = request.json['password']
        except Exception as KeyError:
            error = KeyError.args
            return jsonify(status='failed', msg = f'{error[0]} field is missing in your request'), 400

        check_admin_from_student = Student.query.filter_by(student_id=admin_id).first()
        check_admin_from_admin = Admin.query.filter_by(admin_id=admin_id).first()


        if check_admin_from_student or check_admin_from_admin:
            return jsonify(status='failed', msg='ID has been registered by another user')

        admin = Admin(
            
            first_name = first_name,
            last_name = last_name,
            admin_id =admin_id,
        )
        
        admin.hash_password(password)

        db.session.add(admin)
        db.session.commit()

        return jsonify(status = 'success', msg = 'admin registered successfully')



@sms.route('/student/feedback', methods= ['POST'])
@jwt_required()
@cross_origin()
def student_feedback():
    feedback = request.json['feedback']
    student_id = get_jwt_identity()

    student_id = Student.query.filter_by(student_id=student_id).first()

    feedback_submit = FeedBack(
        feedback = feedback,
        student = student_id 
    )

    db.session.add(feedback_submit)
    db.session.commit()

    return jsonify(status='success', msg='feedback submitted successfully')


@sms.route('/feedbacks')
@cross_origin()
def feedbacks():
    feedbacks = FeedBack.query.all()
    
    serialized_feedback = [*map(serialize_feedback, feedbacks)]
    return jsonify(status='success', feedbacks=serialized_feedback)



@sms.route('/student/profile')
@jwt_required()
@cross_origin()
def student_profile():
    student_matric_no = get_jwt_identity()
    student = Student.query.filter_by(student_id=student_matric_no).first()

    student_profile = dict(name=student.last_name + ' ' + student.first_name, matric_no = student.student_id, level=student.level)

    return jsonify(status='success', student_profile=student_profile)

@sms.route('/chat-log')
@cross_origin()
def chat_log():
    matric_no = request.args.get('matric_no')
    student = Student.query.filter_by(student_id = matric_no).first()
    logs = ChatLog.query.filter_by(student=student).all()
    serialized_logs = [*map(log_serializer, logs)]

    return jsonify(status='success', log = serialized_logs)


@sms.route('/download/<path:filename>',methods=['GET'])
def download(filename):
    

    filepath = os.path.join(os.path.join(os.getcwd(), 'api'), 'upload') #+ '\uploads'
    #filepath = filepath, 'upload')
    
    return send_from_directory(filepath, filename)



