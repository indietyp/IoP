import os
import json
import time
import socket
import inspect
from IoP import app
from copy import deepcopy
from models.main import db
from models.plant import *
from models.sensor import *
from peewee import BaseModel
from inspect import isfunction
from tools.mesh import MeshTools
from models.security import KeyChain
from settings.database import DATABASE_NAME
from mesh_network.daemon import MeshNetwork
from tools.security import KeyChain as keychain
from flask import redirect, url_for, render_template, session, request


def index():
  return 'placeholder'


@app.route('/introduction')
def introduction():
  # if 'step' not in session:
  #   session['step'] = 1
  session['step'] = 1

  if session['step'] >= 1:
    session['step'] = 2
    toolchain = MeshTools()
    toolchain.create_dir_if_not_exists('/local/backup')
    toolchain.create_dir_if_not_exists('/var/log/iop')

    if 'mnt' in DATABASE_NAME.split('/'):
      with open('/etc/fstab', 'r') as out:
        cont = True if "# auto inserted by the iop interface" not in out.read() else False

      if cont:
        with open('/etc/fstab', 'a') as out:
          out.write("\n\n# auto inserted by the iop interface\ntmpfs           /mnt/ramdisk    tmpfs   nodev,nosuid,noexec,nodiratime,size=50M   0 0\n")
    else:
      toolchain.create_dir_if_not_exists('/'.join(DATABASE_NAME.split('/')[:-1]))

    MeshNetwork().discover(1)
    time.sleep(3)

    file = os.path.dirname(os.path.realpath(__file__)) + '../../../../mesh_network/discover/main.json'
    if not os.path.isfile(file):
      discover = False
    else:
      with open(file, 'r') as out:
        data = json.loads(out.read())

      discover = False if len([x for x in data if x['registered']]) == 0 else True

    return render_template('init/introduction.jade', content={'get': True, 'discover': discover})
  return 'failed request, I\'m so sorry!'


@app.route('/information')
def information():
  if session['step'] >= 2:
    session['step'] = 3
    return render_template('init/information.jade', content={'get': True})
  return 'failed request, I\'m so sorry!'


@app.route('/create', methods=['POST'])
def create():
  if session['step'] >= 3:
    session['step'] = 4
    required = ['pname', 'plocation', 'pspecies', 'pinterval', 'wname', 'wemail', 'daccount', 'dsmtp', 'dpassword']

    for item in ['t', 'l', 'h', 'm']:
      required.extend([item + 'unit', item + 'min', item + 'max', item + 'persistant'])
    for item in ['th', 'ca', 'op']:
      required.extend([item + 'max', item + 'min'])

    data = deepcopy(request.form)

    if len(list(set(required) - set(data.keys()))) != 0:
      return 'not valid data, hihihihi'
    print(data)

    models = []
    for module in ['plant', 'sensor', 'people', 'security', 'mesh', 'context']:
      exec('import models.' + module)
      models.extend([
          obj for name, obj in inspect.getmembers(
              eval(module), lambda obj: not isfunction(obj) and isinstance(obj, BaseModel) and obj.__name__ != 'Model' and obj.__name__ != 'Base'
          )
      ])
    # peewee create database
    db.create_tables(models)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 80))
    ip = s.getsockname()[0]
    s.close()

    # import data
    person = Person()
    person.name = data['wname']
    person.email = data['wemail']
    person.wizard = True
    person.save()

    plant = Plant()
    plant.name = data['pname'].lower()
    plant.location = data['plocation'].lower()
    plant.species = data['pspecies'].lower()
    plant.interval = int(data['pinterval'])
    plant.person = person
    plant.ip = ip
    plant.localhost = True
    plant.sat_streak = 0
    plant.save()

    encrypted = keychain().encrypt(data['dpassword'])
    password = KeyChain()
    password.secret = encrypted[0]
    password.message = encrypted[1]
    password.application = 'mailer'
    password.save()

    daemon = MailAccount()
    daemon.account = data['daccount']
    daemon.server = data['dsmtp']
    daemon.daemon = True
    daemon.password = password
    daemon.save()

    for raw in ['temperature', 'light', 'humidity', 'moisture']:
      if raw in ['temperature', 'humidity']:
        model = 'DHT22'
      elif raw == 'light':
        model = 'TLS2561'
      else:
        model = 'generic'

      sensor = Sensor()
      sensor.name = raw
      sensor.model = model
      sensor.unit = data[raw[0] + 'unit']
      sensor.min_value = data[raw[0] + 'min']
      sensor.max_value = data[raw[0] + 'max']
      sensor.persistant_offset = data[raw[0] + 'persistant']
      sensor.save()

    all_sensors = ['temperature', 'light', 'humidity', 'moisture']
    hardware_collection = {'led_traffic_light': all_sensors,
                           'led_bar': ['moisture'],
                           'display': ['temperature', 'humidity'],
                           'mailer': all_sensors,
                           'water_pump': ['moisture']}

    for hardware, values in hardware_collection.items():
      current = SensorHardware(label=hardware, function='execute_' + hardware)
      current.save()

      for sensor in values:
        sensor = Sensor.get(name=sensor)
        c = SensorHardwareConnector(hardware=current, sensor=sensor)
        c.save()

    for level in ['threat', 'cautioning', 'optimum']:
      if level == 'threat':
        color = 'red'
      elif level == 'cautioning':
        color = 'yellow'
      else:
        color = 'green'

      satisfaction_level = SensorSatisfactionLevel()
      satisfaction_level.label = level
      satisfaction_level.name_color = color
      satisfaction_level.save()

      for single_sensor in all_sensors:
        obj_sensor = Sensor.get(name=single_sensor)
        plant = Plant.get(localhost=True)

        sensor_satisfaction_value = SensorSatisfactionValue()
        sensor_satisfaction_value.plant = plant
        sensor_satisfaction_value.sensor = obj_sensor
        sensor_satisfaction_value.level = satisfaction_level

        if level == 'threat':
          sensor_satisfaction_value.inherited = True
          sensor_satisfaction_value.min_value = None
          sensor_satisfaction_value.max_value = None
        else:
          sensor_satisfaction_value.min_value = data[level[0:2] + 'min']
          sensor_satisfaction_value.max_value = data[level[0] + 'max']

        sensor_satisfaction_value.save()

    # reboot
    from subprocess import call
    call(["reboot"])

  return 'failed request, I\'m so sorry!'


@app.errorhandler(404)
def page_not_found(*args, **kwagrs):
  return redirect(url_for('introduction'))
