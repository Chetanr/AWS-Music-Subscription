from flask import *
from pprint import pprint
import boto3
import json
import requests
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from decimal import Decimal

app = Flask(__name__)

app.secret_key = "0123456789"

ACCESS_KEY = "ACCESS_KEY"
SECRET_KEY = "SECRET_KEY"

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
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('subscriptions')
    response= query_subscription_db(table)
    if 'Items' in response:
        return render_template('my_subscriptions.html', posts = response, user_name = session['username'])
    else:
        return render_template('my_subscriptions.html', posts = '', user_name = session['username'])

@app.route('/remove', methods = ['POST'])
def remove():
    if request.method == 'POST':
        username = session['username']
        title = request.form['title']
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('subscriptions')  
        try:
            response = table.delete_item(
                Key={
                    'user_name': username,
                    'title': title
                },
            )
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
            else:
                raise
        else:
            response= query_subscription_db(table)
            if 'Items' in response:
                return render_template('my_subscriptions.html', posts = response, user_name = session['username'])
            else:
                return render_template('my_subscriptions.html', posts = '', user_name = session['username'])

def query_subscription_db(table):
    response = table.query(
        KeyConditionExpression=Key('user_name').eq(session['username'])
    )
    return response


@app.route('/query_area')
def query_area():
    return render_template('query_area.html', user_name = session['username'], posts = '')

@app.route('/back')
def back():
    return render_template('main_page.html', user_name = session['username'])

@app.route('/query_music', methods = ['POST'])
def query_music():
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        artist = request.form['artist']
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('music')
        try:
            response = table.get_item(Key={'title': title, 'artist' : artist})
        except ClientError as e:
            return render_template('query_area.html', posts = '',user_name = session['username'])
        if 'Item' in response:
            return render_template('query_area.html', posts = response,user_name = session['username'])
        else:
            return render_template('query_area.html', posts = '', user_name = session['username'])


@app.route('/subscribe', methods = ['POST'])
def subscribe():
    if request.method == "POST":
        title = request.form['title']
        artist = request.form['artist']
        year = request.form['year']
        # app.logger.info(title)
        # app.logger.info(artist)
        # app.logger.info(year)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('subscriptions')
        table.put_item(
            Item = {
            'title': title,
            'user_name': session['username'],
            'artist': artist,
            'year': year
        })
        response = query_subscription_db(table)
        if 'Items' in response:
            return render_template('my_subscriptions.html', posts = response, user_name = session['username'])
        else:
            return render_template('query_ares.html', posts = '', user_name = session['username'])

@app.route('/logout')
def logout():
    session.clear()  
    return render_template('login.html')

@app.route('/register_user', methods = ['POST'])
def register_user():
    if request.method == "POST":
        username = request.form['user']
        password = request.form['password']
        email = request.form['email']
        result = check_user(email)
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
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('music')
    for music in music_list['songs']:
        upload_bucket(music['img_url'])
        table.put_item(Item=music)
    return table

def upload_bucket(url):
    r = requests.get(url, stream=True)
    session = boto3.Session()
    s3 = session.resource('s3')
    bucket_name = 's3793263-bucket'
    bucket = s3.Bucket(bucket_name)
    key = url
    bucket.upload_fileobj(r.raw, key)

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
            # time.sleep(5)
            # temp2 = load_music_data()
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
