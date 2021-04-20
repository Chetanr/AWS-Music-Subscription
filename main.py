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


# from http import client
# from google.auth import app_engine
from google.cloud import bigquery
from flask import *
from flask.helpers import url_for
from google.auth.transport import requests
from google.cloud import datastore, storage
from google.cloud.storage import client
import google.oauth2.id_token

app = Flask(__name__)

@app.route('/one')
def one():
    bigquery_client = bigquery.Client()
    query = """
        SELECT time_ref, value FROM `chetan-r-project2.task_2_1.task2_1` order by value desc LIMIT 10
        """
    result = bigquery_client.query(query)
    return render_template('one.html', results = result)

@app.route('/two', methods = ['POST'])
def two():
    return "hi"

@app.route('/three', methods = ['POST'])
def three():
    return "hi"

@app.route('/')
def root():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
