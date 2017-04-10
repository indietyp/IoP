import json
import datetime
import platform
import urllib.request
import urllib.parse
from tools.main import VariousTools
from flask import Flask, session, request

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.jinja_env.auto_reload = True
app.secret_key = 'uyfo2346tr3r3urey8f138r9pfr1vy3ofydv'
database = VariousTools.verify_database()

if platform.system() in ['Windows', 'Darwin']:
  database = False
database = False

if database:
  # not rest api compliant? - speed?
  @app.after_request
  def host_verification(response):
    if 'host' not in request.cookies:
      from mesh_network.dedicated import MeshDedicatedDispatch
      from models.plant import Plant

      local = Plant.get(localhost=True)
      if not local.host:
        host = Plant.get(host=True)
        host.host = False
        host.save()
        local.host = True
        local.save()

        MeshDedicatedDispatch().update('host', local.uuid)
      response.set_cookie('host', 'easteregg', max_age=5 * 60)
    return response

  def init():
    with urllib.request.urlopen('http://127.0.0.1:2902/plants?select=satisfaction,sensorsatisfaction,normal&dict=false') as response:
      information = json.loads(response.read().decode('utf8'))['content']

    plants = information['normal']
    satisfaction = information['satisfaction']
    detailed = information['sensorsatisfaction']

    # dirty hotfix (don't like it at all)
    head = "<div class='header'>Overview!</div><div class='content'>"
    tail = "</div>"

    for plant in plants:
      overview = head
      levels = detailed[plant[0]]
      for level in [['optimum', '#21ba45'], ['cautioning', '#fbbd08'], ['threat', '#db2828']]:
        if level[0] in levels:
          overview += """<div style='display:flex; align-items:center'>
                            <svg style='padding-right:10px;margin-right:10px' height='20' width='20'>
                              <circle cx='10' cy='10' r='8' fill='""" + level[1] + """'></circle>
                            </svg>"""
          for sensor in levels[level[0]]:
            overview += sensor + ", "
          overview = overview[:-2] + "<div style='flex-grow:1' /></div>"
      overview += tail
      detailed[plant[0]] = overview

    return {'plants': plants,
            'satisfaction': satisfaction,
            'satisfaction_level': detailed,
            'int': int,
            'str': str}

  def set_uuid():
    for u_plant in init()['plants']:
      if session['plant'] in u_plant:
        session['p_uuid'] = u_plant[0]

  def init_overview():
    # get plant specific stuff
    query = urllib.parse.urlencode({'select': 'created_at,survived,location'})
    with urllib.request.urlopen('http://127.0.0.1:2902/plants/{}?{}'.format(session['p_uuid'], query)) as response:
      data = json.loads(response.read().decode('utf8'))['content']

    created_at = data['created_at']
    survived = data['survived']
    location = data['location']

    # get responsible stuff!
    query = urllib.parse.urlencode({'select': 'full'})
    with urllib.request.urlopen('http://127.0.0.1:2902/plants/{}/responsible?{}'.format(session['p_uuid'], query)) as response:
      responsible = json.loads(response.read().decode('utf8'))['content']

    query = urllib.parse.urlencode({'select': 'average,online'})
    with urllib.request.urlopen('http://127.0.0.1:2902/plants/{}/status?{}'.format(session['p_uuid', query])) as response:
      data = json.loads(response.read().decode('utf8'))['content']

    average_percent = data['average']
    average_online = data['online']

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
    query = urllib.parse.urlencode({'select': 'current,range'})
    with urllib.request.urlopen('http://127.0.0.1:2902/plants/{}/sensor/{}?{}'.format(session['p_uuid'], session['sensor'], query)) as response:
      data = json.loads(response.read().decode())['content']

    current_data = data['current']
    sensor_color_ranges = data['range']

    query = urllib.parse.urlencode({'select': 'range,unit'})
    with urllib.request.urlopen('http://127.0.0.1:2902/sensor/{}?{}'.format(session['sensor'], query)) as response:
      data = json.loads(response.read().decode())['content']

    sensor_range = data['range']
    unit = data['unit']

    # retrieve recent data
    query = urllib.parse.urlencode({'select': 'extreme', 'max': 'true', 'backlog': 'true'})
    with urllib.request.urlopen('http://127.0.0.1:2902/plants/{}/sensor/{}?{}'.format(session['p_uuid'], session['sensor'], query)) as response:
      today_high_data = json.loads(response.read().decode())['content']
    if datetime.date.fromtimestamp(today_high_data['t']) == datetime.date.today():
      recent_date = 'Today'
    else:
      recent_date = datetime.date.fromtimestamp(today_high_data['t']).strftime('%d. %b %Y')
    today_high_data['t'] = datetime.datetime.fromtimestamp(today_high_data['t']).strftime('%H:%M')

    query = urllib.parse.urlencode({'select': 'extreme', 'max': 'false', 'backlog': 'true'})
    with urllib.request.urlopen('http://127.0.0.1:2902/plants/{}/sensor/{}?{}'.format(session['p_uuid'], session['sensor'], query)) as response:
      today_low_data = json.loads(response.read().decode())['content']
    today_low_data['t'] = datetime.datetime.fromtimestamp(today_low_data['t']).strftime('%H:%M')
    today_difference = abs(round(today_high_data['v'] - today_low_data['v'], 1))

    # retrieve extremes ever! YAY!
    query = urllib.parse.urlencode({'select': 'extreme', 'max': 'true', 'ever': 'true'})
    with urllib.request.urlopen('http://127.0.0.1:2902/plants/{}/sensor/{}?{}'.format(session['p_uuid'], session['sensor'], query)) as response:
      ever_high_data = json.loads(response.read().decode())['content']
    ever_high_data['t'] = datetime.datetime.fromtimestamp(ever_high_data['t']).strftime('%d. %b %Y')

    query = urllib.parse.urlencode({'select': 'extreme', 'max': 'false', 'ever': 'true'})
    with urllib.request.urlopen('http://127.0.0.1:2902/plants/{}/sensor/{}?{}'.format(session['p_uuid'], session['sensor'], query)) as response:
      ever_low_data = json.loads(response.read().decode())['content']
    ever_low_data['t'] = datetime.datetime.fromtimestamp(ever_low_data['t']).strftime('%d. %b %Y')
    ever_difference = abs(round(ever_high_data['v'] - ever_low_data['v'], 1))

    return {'sensor_unit': str(unit),
            'sensor_color_ranges': sensor_color_ranges,
            'current_data': current_data,
            'sensor_range': sensor_range,
            'ever_data': {
                'high': ever_high_data,
                'low': ever_low_data,
                'difference': ever_difference},
            'recent_data': {
                'high': today_high_data,
                'low': today_low_data,
                'difference': today_difference,
                'date': recent_date}
            }

  import IoP.views.general
  import IoP.views.plants
  import IoP.views.get.plants
  import IoP.views.get.plants_ext
  import IoP.views.get.general
else:
  import IoP.init.views.main
