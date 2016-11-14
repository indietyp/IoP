from flask import Flask, session, render_template
import urllib.request
import sys
import json
import datetime
from bson import json_util

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.secret_key = 'uyfo2346tr3r3urey8f138r9pfr1vy3ofydv'


def init():
  # get smiles! YOYOYOYOYOYOYOYOYO! :D
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plants/name') as response:
    plants = json.loads(response.read().decode('utf8'))

  with urllib.request.urlopen('http://127.0.0.1:2902/get/plants/satisfaction') as response:
    satisfaction = json.loads(response.read().decode('utf8'))

  return {'plants': plants,
          'satisfaction': satisfaction,
          'int': int,
          'str': str}


def set_uuid():
  for u_plant in init()['plants']:
    if session['plant'] in u_plant:
      session['p_uuid'] = u_plant[0]


def init_overview():
  # get created at date
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/created_at') as response:
    created_at = json.loads(response.read().decode('utf8'), object_hook=json_util.object_hook)

  # get time survived
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/survived') as response:
    survived = json.loads(response.read().decode('utf8'), object_hook=json_util.object_hook)['data']

  # get location
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/location') as response:
    location = json.loads(response.read().decode('utf8'))

  # get responsible stuff!
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/responsible') as response:
    responsible = json.loads(response.read().decode('utf8'))

  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/status/average') as response:
    average_percent = json.loads(response.read().decode('utf8'))

  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/status/online') as response:
    average_online = json.loads(response.read().decode('utf8'))

  return {'created_at': created_at,
          'location': location,
          'survived': str(survived),
          'responsible': responsible,
          'average_percent': average_percent,
          'average_online': average_online}


def init_sensor():
  # if recent data is far back, then time is getting really slow -> ~ 2 months == 4 seconds, ~ 3 days == 0.5 seconds
  # ms = datetime.datetime.now().timestamp()
  # get current_data
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/sensor/' + session['sensor'] + '/data/current') as response:
    current_data = json.loads(response.read().decode('utf8'))

  with urllib.request.urlopen('http://127.0.0.1:2902/get/sensor/' + session['sensor'] + '/range') as response:
    sensor_range = json.loads(response.read().decode('utf8'))

  # get recent data (don't need to be today -> if not signal?)
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/sensor/' + session['sensor'] + '/high/today/yes') as response:
    today_high_data = json.loads(response.read().decode('utf8'))
    if datetime.date.fromtimestamp(today_high_data['t']) == datetime.date.today():
      recent_date = 'Today'
    else:
      recent_date = datetime.date.fromtimestamp(today_high_data['t']).strftime('%d. %b %Y')
    today_high_data['t'] = datetime.datetime.fromtimestamp(today_high_data['t']).strftime('%H:%M')

  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/sensor/' + session['sensor'] + '/low/today/yes') as response:
    today_low_data = json.loads(response.read().decode('utf8'))
    today_low_data['t'] = datetime.datetime.fromtimestamp(today_low_data['t']).strftime('%H:%M')

  today_difference = round(today_high_data['v'] - today_low_data['v'], 1)

  # get ever data
  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/sensor/' + session['sensor'] + '/high/ever') as response:
    ever_high_data = json.loads(response.read().decode('utf8'))
    ever_high_data['t'] = datetime.datetime.fromtimestamp(ever_high_data['t']).strftime('%d. %b %Y')

  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/sensor/' + session['sensor'] + '/low/ever') as response:
    ever_low_data = json.loads(response.read().decode('utf8'))
    ever_low_data['t'] = datetime.datetime.fromtimestamp(ever_low_data['t']).strftime('%d. %b %Y')

  ever_difference = round(ever_high_data['v'] - ever_low_data['v'], 1)

  with urllib.request.urlopen('http://127.0.0.1:2902/get/sensor/' + session['sensor'] + '/unit') as response:
    unit = json.loads(response.read().decode('utf8'))['unit']
    # print(str(unit), file=sys.stdout)

  with urllib.request.urlopen('http://127.0.0.1:2902/get/plant/' + session['p_uuid'] + '/sensor/' + session['sensor'] + '/range') as response:
    sensor_color_ranges = json.loads(response.read().decode('utf8'))


  # ms2 = datetime.datetime.now().timestamp() - ms
  # print(str(ms2), file=sys.stdout)

  return {'sensor_unit': str(unit), 'sensor_color_ranges': sensor_color_ranges, 'current_data': current_data, 'sensor_range': sensor_range, 'ever_data': {'high': ever_high_data, 'low': ever_low_data, 'difference': ever_difference}, 'recent_data': {'high': today_high_data, 'low': today_low_data, 'difference': today_difference, 'date': recent_date}}


import IoP.views.general
import IoP.views.plants
import IoP.views.get.plants
import IoP.views.get.plants_ext
import IoP.views.get.general
