from IoP import app, init_overview, init_sensor, set_uuid, init
from flask import render_template, session, request
import sys
import urllib.request
import urllib.parse
import json


@app.route('/get/notification/message/names', methods=['POST'])
def get_message_ips():
  with urllib.request.urlopen('http://localhost:2902/get/discovered/0/names') as response:
    return response.read().decode('utf8')


@app.route('/get/notification/message/content', methods=['POST'])
def get_message_content():
  message_uuid = request.form['uuid']

  with urllib.request.urlopen('http://localhost:2902/get/message/' + message_uuid + '/content') as response:
    return response.read().decode('utf8')


@app.route('/submit/notification/message', methods=['POST'])
def insert_message():
  return json.dumps({'info': 'to be included'})
