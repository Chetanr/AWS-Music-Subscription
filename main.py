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
from decimal import Decimal



app = Flask(__name__)

app.secret_key = "0123456789"

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
                    return response['Item']['user_name']
        return False

@app.route('/subscription')
def subscription():
    return "subscription"

@app.route('/query_area')
def query_area():
    return render_template('query_area.html', user_name = session['username'])

@app.route('/query_music', methods = ['POST'])
def query_music():
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        artist = request.form['artist']
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('music')
        response = table.get_item(Key={'title': title, 'artist' : artist})
        if 'Item' in response:
            return render_template('query_area.html', posts = response)
            return response['Item']
    return response


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


def create_music_database():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.create_table(
        TableName = "music",
        KeySchema = [
            {
                'AttributeName': 'title',
                'KeyType': 'HASH'
            },
             {
                'AttributeName': 'artist',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'title',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'artist',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

def load_music_data():
    with open("a2.json") as json_file:
        music_list = json.load(json_file, parse_float=Decimal)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('music')
    for music in music_list['songs']:
        app.logger.info(music['title'])
        # app.logger.info(music['artist'])
        # app.logger.info(music['year'])
        # app.logger.info(music['web_url'])
        # app.logger.info(music['image_url'])
        table.put_item(Item=music)
    return table

def check_user(email):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('login')
    try:
        response1 = table.get_item(Key={'email': email})
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
            return render_template('login.html', invalid = "email or password is invalid")
        else:
            # temp = create_music_database()
            # app.logger.info(temp)
            # temp = load_music_data()
            # app.logger.info(temp)
            session['username'] = result
            app.logger.info(session['username'])
            return render_template('main_page.html', user_name = result)

#starting point of the application
@app.route('/')
def root():
    return render_template('login.html')



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
