from flask import Flask, session, render_template
import urllib.request
import sys
import json
from bson import json_util

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.secret_key = 'uyfo2346tr3r3urey8f138r9pfr1vy3ofydv'

def init():
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plants/name') as response:
    plants = json.loads(response.read().decode('utf8'))
  return {'plants': plants}

def init_overview():
  # get created at date
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['plant'] + '/created_at') as response:
    created_at = json.loads(response.read().decode('utf8'), object_hook=json_util.object_hook)

  # get time survived
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['plant'] + '/survived') as response:
    survived = json.loads(response.read().decode('utf8'), object_hook=json_util.object_hook)

  # get location
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['plant'] + '/location') as response:
    location = json.loads(response.read().decode('utf8'))

  # get responsible stuff!
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['plant'] + '/responsible') as response:
    responsible = json.loads(response.read().decode('utf8'))
  return {'created_at': created_at, 'location': location, 'survived': str(survived), 'responsible': responsible}

def init_sensor():
  # get current_data
  with urllib.request.urlopen('http://localhorst:2902/get/plant/' + session['plant'] + '/sensor/' + session['sensor'] + '/current') as response:
    current_data = json.loads(response.read().decode('utf8'))
  return {'current_data': current_data}

import IoP.views.general
import IoP.views.plants
import IoP.views.get.plants
import IoP.views.get.general
