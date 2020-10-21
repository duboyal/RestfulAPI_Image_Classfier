from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import numpy
import tensorflow as tf
import requests
import subprocess
import json


app = Flask(__name__)
api = Api(app)

#----------
"""
will see if this works 
just making some global variables to take in from form data
"""
username1=''
password1=''
url1=''
admin1_pw=''
amount1=0

@app.route('/', methods=['GET', 'POST'])
def form():
    return render_template('form.html')

@app.route('/hello', methods=['GET', 'POST'])
def hello():
    #username,password, url, admin_pw,amount
    username1 =request.form['username']
    password1 =request.form['password']
    url1 =request.form['url']
    admin1_pw =request.form['admin_pw']
    amount1 =request.form['amount']

    #could think about "make_response" or "jsonify" wrapping around render template?
    #honestly this request.form could be enough?
    #could look at flask sessions or cookies

    return render_template('greeting.html', username=request.form['username'], password=request.form['password'], url=request.form['url'],admin_pw=request.form['admin_pw'],amount=request.form['amount'])


#-----

client = MongoClient("mongodb://db:27017")
db = client.IRG
users = db["Users"]

def UserExist(username):
    if users.find({"Username":username}).count() == 0:
        return False
    else:
        return True

class Register(Resource):
    def post(self):
        #Step 1 is to get posted data by the user
        postedData = request.get_json()

        #Get the data
        username = username1 #postedData["username"]
        password = password1 #postedData["password"] #"123xyz"

        if UserExist(username):
            retJson = {
                'status':301,
                'msg': 'Invalid Username'
            }
            return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #Store username and pw into the database
        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Tokens":10
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }
        return jsonify(retJson)

def verifyPw(username, password):
    if not UserExist(username):
        return False

    hashed_pw = users.find({
        "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def generateReturnDictionary(status, msg):
    retJson = {
        "status": status,
        "msg": msg
    }
    return retJson

def verifyCredentials(username, password):
    if not UserExist(username):
        return generateReturnDictionary(301, "Invalid Username"), True

    correct_pw = verifyPw(username, password)

    if not correct_pw:
        return generateReturnDictionary(302, "Incorrect Password"), True

    return None, False


class Classify(Resource):
    def post(self):

        #figure out how to jsonify the render_template
        #even though they do 

        postedData = request.get_json()

        username = username1 #postedData["username"]
        password = password1 #postedData["password"]
        url = url1 #postedData["url"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        tokens = users.find({
            "Username":username
        })[0]["Tokens"]

        if tokens<=0:
            return jsonify(generateReturnDictionary(303, "Not Enough Tokens"))

        r = requests.get(url)
        retJson = {}
        with open('temp.jpg', 'wb') as f:
            f.write(r.content)
            proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file=./temp.jpg', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            ret = proc.communicate()[0]
            proc.wait()
            with open("text.txt") as f:
                retJson = json.load(f)


        users.update({
            "Username": username
        },{
            "$set":{
                "Tokens": tokens-1
            }
        })

        return retJson


class Refill(Resource):
    def post(self):
        postedData = request.get_json()

        username = username1 #postedData["username"]
        password = password1 #postedData["admin_pw"]
        amount = amount1 #postedData["amount"]

        if not UserExist(username):
            return jsonify(generateReturnDictionary(301, "Invalid Username"))

        correct_pw = "abc123"
        if not password == correct_pw:
            return jsonify(generateReturnDictionary(302, "Incorrect Password"))

        users.update({
            "Username": username
        },{
            "$set":{
                "Tokens": amount
            }
        })
        return jsonify(generateReturnDictionary(200, "Refilled"))


api.add_resource(Register, '/register')
api.add_resource(Classify, '/classify')
api.add_resource(Refill, '/refill')

if __name__=="__main__":
    app.run(host='0.0.0.0')
