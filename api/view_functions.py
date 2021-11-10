import json
from os import name 
import numpy as np
import numpy as np
from .models import Student
import random
import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import json
from keras.models import load_model

lemmatizer = WordNetLemmatizer()




model = load_model("./api/model/chatbot_model.h5")
intents = json.loads(open("./api/model/chatbot.json").read())
words = pickle.load(open("./api/model/words.pkl", "rb"))
classes = pickle.load(open("./api/model/classes.pkl", "rb"))


def search_engine(query, search_param):
    if search_param:
        query = query.filter(
            (Student.student_id.contains(search_param)) | (Student.first_name.contains(search_param)) | (Student.last_name.contains(search_param)))
        return query.all()


def serialize_student(student_query):
    return dict(name=student_query.last_name + ' ' + student_query.first_name, matric_number=student_query.student_id, level = student_query.level)


def serialize_feedback(query):
    return dict(feedback=query.feedback, name = query.student.first_name  + ' ' + query.student.last_name, matric_no = query.student.student_id, read_status=query.read)


# chat functionalities
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    print(len(p))
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    tag = ints[0]["intent"]
    list_of_intents = intents_json["intents"]
    for i in list_of_intents:
        if i["tag"] == tag:
            result = random.choice(i["responses"])
            print(result)
            break
    return result