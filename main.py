# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from flask import *
from pprint import pprint
import boto3
from botocore.exceptions import ClientError



app = Flask(__name__)


def check_login(user, password, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('login')
        try:
            response = table.get_item(Key={'email': user})
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in response:
                if(response['Item']['password'] == password):
                    return True
        return False


@app.route('/logout')
def logout():
    session.clear() 
    # app.logger.info(session['username']) 
    return render_template('login.html')

@app.route('/register_user', methods = ['POST'])
def register_user():
    if request.method == "POST":
        username = request.form['user']
        password = request.form['password']
        email = request.form['email']
        result = check_user(username, email)
        if(result is True):
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('login')
            table.put_item(
                Item = {
                'email': email,
                'user_name': username,
                'password': password
                }
            )
            return render_template('login.html')
        return render_template('register.html', invalid = "The email already exists")


def check_user(email):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('login')
    try:
        response1 = table.get_item(Key={'email': email})
        # response2 = table.get_item(Key={'user_name': username})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        if 'Item' in response1:
            return False
    return True



@app.route('/register')
def register():
    return render_template('register.html')



@app.route('/login', methods = ['POST'])
def login():
    if request.method == 'POST':
        username = request.form['user']
        password = request.form['password']
        result = check_login(username,password)
        app.logger.info(result)
        if (result is False):
            session['username'] = username
            session['password'] = password
            return render_template('login.html', invalid = "email or password is invalid")
        else:
            return render_template('main_page.html')

#starting point of the application
@app.route('/')
def root():
    return render_template('login.html')



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
