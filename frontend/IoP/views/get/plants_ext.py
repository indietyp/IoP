from IoP import app, init_overview, init_sensor, set_uuid, init
from flask import render_template, session, request
import sys
import urllib.request
import urllib.parse
import json


@app.route('/get/notification/message/names', methods=['POST'])
def get_message_name():
  with urllib.request.urlopen('http://localhost:2902/get/messages/names') as response:
    output = response.read().decode('utf8')
  return output


@app.route('/get/notification/message/content', methods=['POST'])
def get_message_content():
  message_uuid = request.form['uuid']

  with urllib.request.urlopen('http://localhost:2902/get/message/' + message_uuid + '/content') as response:
    return response.read().decode('utf8')


@app.route('/submit/notification/message', methods=['POST'])
def insert_message():
  data = urllib.parse.urlencode({'name': request.form['name'], 'text': request.form['message'], 'plant': session['p_uuid']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/notification/message', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))
  with urllib.request.urlopen('http://localhost:2902/update/notification/message') as response:
    return response.read().decode('utf8')


@app.route('/remove/responsible', methods=['POST'])
def delete_responsible():
  with urllib.request.urlopen('http://localhost:2902/delete/responsible/' + request.form['uuid']) as response:
    data = response.read().decode('utf8')

  return data


@app.route('/change/responsible/wizard')
def change_responsible_wizard():
  data = urllib.parse.urlencode({'replacement': request.form['uuid']}).encode('ascii')
  req = urllib.request.Request('http://localhost:2902/update/responsible/wizard', data)
  with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf8'))

  return data
