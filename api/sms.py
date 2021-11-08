from flask import Blueprint, jsonify, request, make_response, g
from keras.utils.io_utils import path_to_string
from tensorflow.python.eager.context import context
from .extensions import db
from .models import Student, Admin
import json
from datetime import datetime
from datetime import date
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from .extensions import jwt
from flask_cors import CORS, cross_origin
from collections import Counter
from .view_functions import (
                            search_engine, serialize_student, predict_class,
                            getResponse, 
                            )
from .model.train import train_bot
from keras.models import load_model


#   initialize the blueprint for the API version1

sms = Blueprint('sms', __name__)
CORS(sms, resources={r"/sms/*": {"origins":"*"}})
intents = json.loads(open("./api/model/chatbot.json").read())




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

        check_student = Student.query.filter_by(student_id=matric_no).first()

        if check_student:
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
    file.save(f'./api/download/{file.filename}')


    return jsonify(status='success', msg='uploaded successfully')


@sms.route('/train-bot', methods = ['POST'])
@cross_origin()
def train():

    tag = request.json['tag']
    patterns = request.json['patterns'].split(',')
    responses = request.json['responses'].split(',')

    if (tag == '' or  patterns == '' or responses == ''):
        return jsonify(status='failed', msg = "tag, patterns or responses can't be empty")

    new_intent = dict(tag=tag, patterns=patterns, responses=responses, context=[''])

    with open("./api/model/chatbot.json" , 'r') as bot_intent:
        intents = json.load(bot_intent)

    intents['intents'].append(new_intent)

    with open("./api/model/chatbot.json", 'w') as new_file:
	    json.dump(intents, new_file)
    
    train = train_bot()
   
    if train:
        model = load_model("./api/model/chatbot_model.h5")

        '''try:
            predict_message = predict_class('test', model)
        except:
            with open("./api/model/chatbot.json" , 'r') as bot_intent:
                intents = json.load(bot_intent)
                intents['intents'].pop(-1)
            with open("./api/model/chatbot.json", 'w') as new_file:
	            json.dump(intents, new_file)
            return jsonify(status='failed', msg='unknown error occured. Kindly retrain your bot')'''
            
        return jsonify(status='success', msg = 'bot updated successfully')


@sms.route('/train-bot-with-no-update')
@cross_origin()
def train_bot_with_no_update():
    train = train_bot()
    if train:
        return jsonify(status='success', msg = 'bot updated successfully')


@sms.route('/chat')
@cross_origin()
def chat_bot():
    message = request.args.get('message')
    print(message)

    model = load_model("./api/model/chatbot_model.h5")
    

    predict_message = predict_class(message, model)
    bot_response = getResponse(predict_message, intents)

    return jsonify(status='success', response=bot_response)

    