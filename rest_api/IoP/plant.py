from IoP import app

import sys
import datetime
from uuid import UUID
from copy import deepcopy
from flask import request
from models.mesh import MeshObject
from peewee import Clause, fn, SQL
from playhouse.shortcuts import model_to_dict
from mesh_network.dedicated import MeshDedicatedDispatch
from models.plant import Person, Plant, PlantNetworkUptime, PlantNetworkStatus
from IoP.tooling import get_sensor_data_high_low, copy_model_instance_from_localhost, data_formatting, time_request_from_converter
from models.sensor import Sensor, SensorData, SensorDataPrediction, SensorSatisfactionValue, SensorSatisfactionLevel, SensorCount, SensorStatus
slave_supported = ['moisture']


@app.route('/plants', methods=['GET', 'PUT'])
def plants():
  # GET: select: minimal, normal, detailed, extensive, master, satisfaction, default (normal)
  # GET: dict: Boolean
  if request.method == 'GET':
    selected = request.args.get('select', '').lower()
    mode = request.args.get('dict', '').lower()

    if selected == 'default' or selected == '':
      selected = 'normal'

    mode = True if mode == 'true' else False
    if mode not in [True, False] or selected not in ['minimal', 'normal', 'detailed', 'extensive']:
      return data_formatting(400)

    output = []
    plants = Plant.select().dicts()
    if selected == 'master':
      plants = plants.where(Plant.role == 'master')
    list(plants)

    if selected != 'satisfaction':
      for plant in plants:
        used = []
        if selected in ['minimal', 'normal', 'detailed', 'extensive', 'master']:
          used.append('uuid')

        if selected in ['normal', 'detailed', 'extensive', 'master']:
          used.append('name')

        if selected in ['detailed', 'extensive', 'master']:
          used.append('role')
          used.append('localhost')

        if selected in ['extensive', 'master']:
          used.append('active')

        data = [] if not mode else {}
        for use in used:
          if isinstance(plant[use], UUID):
            plant[use] = str(plant[use])

          if not mode:
            data.append(plant[use])
          else:
            data[use] = plant[use]
        output.append(data)
    elif selected == 'satisfaction':
      output = {}
      sensors = Sensor.select()
      for plant in plants:
        host = None
        if plant.role != 'master':
          host = Plant.get(Plant.uuid == plant.role)

        statuses = []
        for sensor in sensors:
          selected = plant
          if sensor.name not in slave_supported and host is not None:
            selected = host

          status = SensorStatus.get(SensorStatus.sensor == sensor, SensorStatus.plant == selected)
          inserted = 1
          if status.level.label == 'threat':
            inserted = 3
          elif status.level.label == 'cautioning':
            inserted = 2
          statuses.append(inserted)

        maximum = max(statuses)
        label = 'optimum'
        if maximum == 3:
          label = 'threat'
        elif maximum == 2:
          label = 'cautioning'

        output[str(plant.uuid)] = {'streak': plant.sat_streak, 'name': label}

    return data_formatting(data=output)
  else:
    # PUT: register: true
    data = [x.lower() for x in request.data]

    if 'register' in data:
      register = True if data['register'] == 'true' else False
    else:
      register = False

    plants = list(Plant.select(Plant.ip == data['ip']).dicts())

    discovered = MeshObject.get(ip=data['ip'])
    if plants.count() == 0:
      return data_formatting(304)

    plant = Plant()
    plant.name = data['name']
    plant.location = data['location']
    plant.species = data['species']
    plant.interval = data['interval']
    plant.person = Person.get(email=data['email'])
    plant.ip = data['ip']
    plant.sat_streak = 0

    if 'uuid' in data:
      plant.uuid = data['uuid']
    if 'persistant_hold' in data:
      plant.persistant_hold = data['persistant_hold']

    if not discovered.master:
      if 'role' not in data:
        master = Plant.get(localhost=True)
      else:
        master = Plant.get(uuid=data['role'])

      plant.role = str(master.uuid)

    plant.save()

    local_plant = Plant.get(localhost=True)
    for model in [SensorStatus, SensorCount, SensorSatisfactionValue, PlantNetworkUptime]:
      copy_model_instance_from_localhost(plant, model, model.plant == local_plant)

    for count in list(SensorCount.select().where(SensorCount.plant == plant)):
      count.count = 0
      count.save()

    for uptime in list(PlantNetworkUptime.select().where(PlantNetworkUptime.plant == plant)):
      uptime.overall = 0
      uptime.current = 0
      uptime.save()

    if register:
      MeshDedicatedDispatch().register(plant)

    return data_formatting()


@app.route('/plants/<p_uuid>', methods=['GET', 'POST'])
def plant(p_uuid):
  if request.method == 'GET':
    # GET: select: intervals, created_at, type/species, survived, location, full, default (full)
    selected = request.args.get('select', '').lower()
    selectable = ['intervals', 'created_at', 'type', 'species', 'survived', 'location', 'full']

    if selected in ['', 'default']:
      selected = 'full'

    if selected == 'type':
      selected = 'species'

    if selected not in selectable:
      return data_formatting(400)

    plant = list(Plant.select(Plant, fn.CAST(Clause(fn.strftime('%s', Plant.created_at), SQL('AS INT'))).alias('created_at')).dicts())[0]
    plant['uuid'] = str(plant['uuid'])

    if selected not in ['full', 'intervals']:
      output = {selected: plant[selected]}
    elif selected in ['intervals']:
      output = {'connection_lost': plant['connection_lost'],
                'non_persistant': int(plant['persistant_hold'] * 5 / 60 / 24),
                'notification': plant['interval']}
    else:
      output = plant

    return data_formatting(data=output)
  elif request.method == 'POST':
    # POST: replace: name, type, location, ranges, responsible
    # POST: mode: add, reset, online, offline
    # POST: new: DATA

    data = deepcopy(request.form)
    keys = list(data.keys())
    replaceable = ['name', 'species', 'location', 'ranges', 'responsible', 'satisfaction', 'alive', 'notification', 'connection-lost', 'non-persistant']
    # replace = data['replace'].lower()

    if 'type' in keys:
      data['species'] = data['type']
      keys.remove('type')
      keys.append('species')
      del data['type']

    if 'mode' in data:
      mode = 'add' if 'satisfaction' in keys else 'offline'
    else:
      mode = data['mode'].lower()

    if len(set(keys) - set(replaceable)):
      return data_formatting(400)

    plant = Plant.get(uuid=p_uuid)

    if 'name' in keys:
      plant.name = data['name']

    if 'species' in keys:
      plant.species = data['species']

    if 'location' in keys:
      plant.location = data['location']

    if 'ranges' in keys:
      plant = Plant.get(Plant.uuid == p_uuid)
      sensor = Sensor.get(Sensor.name == request.form['sensor'].lower())

      level_yellow = SensorSatisfactionLevel.get(SensorSatisfactionLevel.name_color == 'yellow')
      level_green = SensorSatisfactionLevel.get(SensorSatisfactionLevel.name_color == 'green')

      value_yellow = SensorSatisfactionValue.get(SensorSatisfactionValue.plant == plant,
                                                 SensorSatisfactionValue.sensor == sensor,
                                                 SensorSatisfactionValue.level == level_yellow)

      value_green = SensorSatisfactionValue.get(SensorSatisfactionValue.plant == plant,
                                                SensorSatisfactionValue.sensor == sensor,
                                                SensorSatisfactionValue.level == level_green)

      value_yellow.min_value = int(request.form.getlist('data[]')[0])
      value_green.min_value = int(request.form.getlist('data[]')[1])
      value_green.max_value = int(request.form.getlist('data[]')[2])
      value_yellow.max_value = int(request.form.getlist('data[]')[3])

      value_green.save()
      value_yellow.save()

      MeshDedicatedDispatch().update('plant satisfaction level', plant.uuid)
      if sensor.name == 'moisture' and plant.role != 'master':
        # logger.info('executing slave update')
        information = {'min': value_yellow.min_value, 'max': value_yellow.max_value}
        MeshDedicatedDispatch().slave_update(2, information, plant)

    if 'responsible' in keys:
      person = Person.get(email=data['email'], name=data['name'])
      plant.person = person
      plant.save()

    if 'satisfaction' in keys:
      if mode == 'add':
        plant.sat_streak += 1
      else:
        plant.sat_streak = 1

      plant.save()

    if 'alive' in keys:
      counterpart = 'online' if mode == 'offline' else 'offline'
      status = PlantNetworkStatus.get(name=mode)
      counterpart = PlantNetworkStatus.get(name=counterpart)

      if plant.role == 'master':
        return data_formatting()

      status = PlantNetworkUptime.get(plant=plant, status=status)
      counterpart = PlantNetworkUptime.get(plant=plant, status=counterpart)

      if counterpart.current != 0:
        counterpart.current = 0
        counterpart.save()

      status.current += 1
      status.overall += 1
      status.save()

    if 'notification' in keys:
      _, _, hours = time_request_from_converter(data)
      plant.interval = int(round(hours))

    if 'connection-lost' in keys:
      _, minutes, _ = time_request_from_converter(data)
      plant.connection_lost = int(round(minutes))

    if 'non-persistant' in keys:
      _, minutes, _ = time_request_from_converter(data)
      plant.persistant_hold = int(round(minutes / 5))

    MeshDedicatedDispatch().update('plant', plant.uuid)
    return data_formatting()


@app.route('/plants/<p_uuid>/sensor', methods=['GET'])
def plant_sensors(p_uuid):
  # GET: select: range (default), default
  plant = Plant.get(uuid=p_uuid)
  selected = request.args.get('select', '').lower()
  selectable = ['range', 'default']

  if selected in ['', 'default']:
    selected = 'range'

  if selected not in selectable:
    return data_formatting(400)

  if selected == 'range':
    sensors = Sensor.select()

    output = []
    for sensor in sensors:
      ranges = SensorSatisfactionValue.select() \
                                      .where(SensorSatisfactionValue.plant == plant) \
                                      .where(SensorSatisfactionValue.sensor == sensor)

      tmp = {}
      for spectrum in ranges:
        tmp[spectrum.level.name_color] = {'max': spectrum.max_value, 'min': spectrum.min_value}
        if spectrum.level.name_color == 'red':
          tmp[spectrum.level.name_color] = {'max': sensor.max_value, 'min': sensor.min_value}
      output.append({'settings': tmp, 'sensor': sensor.name})

    return data_formatting(data=output)


@app.route('/plants/<p_uuid>/sensor/<s_uuid>', methods=['GET'])
def plant_sensor(p_uuid, s_uuid):
  # GET: select: latest, prediction, data, current, range, extreme, message
  # GET: max: Boolean (extreme)
  # GET: ever: Boolean (extreme)
  # GET: backlog: Boolean (extreme)
  # GET: start: Integer (data)
  # GET: stop: Integer (data)
  # GET: count: Boolean (data)
  # 'message'
  selected = request.args.get('select', '').lower()
  selectable = ['latest', 'prediction', 'data', 'current', 'range', 'extreme', 'count', 'timespan']

  try:
    sensor = Sensor.get(uuid=s_uuid)
  except:
    sensor = Sensor.get(name=s_uuid)

  plant = Plant.get(uuid=p_uuid)
  if plant.role != 'master' and sensor.name not in slave_supported:
    plant = Plant.get(uuid=plant.role)

  maximum = request.args.get('max', '').lower()
  backlog = request.args.get('backlog', '').lower()
  count = request.args.get('count', '').lower()
  start = request.args.get('start', '').lower()
  stop = request.args.get('stop', '').lower()
  ever = request.args.get('ever', '').lower()

  if selected in ['', 'default']:
    selected = 'data'

  maximum = True if maximum == 'true' else False
  backlog = False if backlog == 'false' else True

  count = True if count == 'true' else False
  if selected != 'timespan':
    start = 0 if start == '' or not start.isdigit() else int(start)
    stop = sys.maxsize if stop == '' or not stop.isdigit() else int(stop)
  else:
    start = datetime.datetime.min if start == '' or not start.isdigit() else datetime.datetime.fromtimezone(int(start))
    stop = datetime.datetime.max if stop == '' or not stop.isdigit() else datetime.datetime.fromtimezone(int(stop))
  ever = True if ever == 'true' else False

  if selected not in selectable:
    return data_formatting(400)

  if selected in ['latest', 'current', 'extreme', 'data', 'count', 'timespan']:
    data = SensorData.select(SensorData.value,
                             SensorData.persistant,
                             fn.CAST(Clause(fn.strftime('%s', SensorData.created_at), SQL('AS INT'))).alias('timestamp')) \
                     .where(SensorData.plant == plant) \
                     .where(SensorData.sensor == sensor) \
                     .order_by(SensorData.created_at.asc()) \
                     .dicts()
  elif selected in ['prediction']:
    data = SensorDataPrediction.select(SensorDataPrediction.value,
                                       fn.CAST(Clause(fn.strftime('%s', SensorDataPrediction.time), SQL('AS INT'))).alias('timestamp')) \
                               .where(SensorDataPrediction.plant == plant) \
                               .where(SensorDataPrediction.sensor == sensor) \
                               .order_by(SensorDataPrediction.created_at.asc()) \
                               .dicts()
  elif selected in ['range']:
    data = SensorSatisfactionValue.select() \
                                  .where(SensorSatisfactionValue.plant == plant) \
                                  .where(SensorSatisfactionValue.sensor == sensor)

  if selected in ['latest', 'current']:
    data = data.order_by(SensorData.created_at.desc()).limit(1)
    output = list(data)[0]
  elif selected == 'prediction':
    output = list(data)
  elif selected == 'range':
    output = {}
    for spectrum in data:
      output[spectrum.level.name_color] = {'max': spectrum.max_value, 'min': spectrum.min_value}
      if spectrum.level.name_color == 'red':
        output[spectrum.level.name_color] = {'max': sensor.max_value, 'min': sensor.min_value}
  elif selected == 'extreme':
    target = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    if backlog and not ever:
      output = None
      while output is None:
        output = get_sensor_data_high_low(plant, sensor, maximum, target)
        target = target - datetime.timedelta(days=1)
    else:
      if ever:
        target = None
      output = get_sensor_data_high_low(plant, sensor, maximum, target)
  elif selected == 'count':
    output = data.count()
  elif selected == 'timespan':
    data = data.where(SensorData.created_at >= start, SensorData.created_at <= stop)
    output = list(data)
  else:
    data = data.order_by(SensorData.created_at.desc()).offset(start).limit(stop - start)
    output = list(data)

  return data_formatting(data=output)


@app.route('/plants/<p_uuid>/responsible', methods=['GET'])
def plant_responsible(p_uuid):
  # GET: select: email, wizard, username, full, default (full)
  selected = request.args.get('select', '').lower()
  selectable = ['email', 'wizard', 'username', 'full']

  responsible = Plant.get(uuid=p_uuid).person
  responsible = model_to_dict(responsible)
  responsible['uuid'] = str(responsible['uuid'])

  if selected in ['', 'default']:
    selected = 'full'

  if selected not in selectable:
    return data_formatting(400)

  if selected != 'full':
    used = [selected, 'uuid']
  else:
    used = list(responsible.keys())

  output = {}
  for key in used:
    if key != 'id':
      output[key] = responsible[key]

  return data_formatting(data=output)


@app.route('/plants/<p_uuid>/status', methods=['GET'])
def plant_status(p_uuid):
  # GET: select: average, online
  selected = request.args.get('select', '').lower()
  selectable = ['average', 'online']
  plant = Plant.get(uuid=p_uuid)

  if selected not in selectable:
    return data_formatting(400)

  if selected == 'average':
    c = Sensor.select().count()
    sensor_count = SensorCount.select() \
                              .where(SensorCount.plant == plant)

    average = {'red': 0, 'yellow': 0, 'green': 0}

    for count in sensor_count:
      average[count.level.name_color] += count.count

    summary = 0
    for key, item in average.items():
      average[key] /= c
      summary += average[key]

    output = {}
    for key, item in average.items():
      try:
        output[key] = [round(item / summary * 100), item]
      except ZeroDivisionError:
        output[key] = [0, item]
  else:
    uptimes = PlantNetworkUptime.select() \
                                .where(PlantNetworkUptime.plant == plant)

    output = {}
    summary = 0

    for uptime in uptimes:
      output[uptime.status.name] = [0, uptime.overall, uptime.current]
      summary += uptime.overall

    for key, uptime in output.items():
      print(type(output[key][1]))
      output[key][0] = round(output[key][1] / summary * 100) if output[key][1] != 0 else 0

    if output == {}:
      output = {'online': [0, 0.0, 0.0], 'offline': [0, 0.0, 0.0]}

    if plant.localhost:
      output = {'online': [100, 1, 1], 'offline': [100, 1, 1]}

  return data_formatting(data=output)


@app.route('/plants/<p_uuid>/message', methods=['GET'])
def plant_message(p_uuid):
  # GET: select: full
  selected = request.args.get('select', '').lower()
  selectable = ['full']
  plant = Plant.get(uuid=p_uuid)

  if selected not in selectable:
    return data_formatting(400)

  message = plant.person.preset
  output = {'uuid': str(message.uuid), 'message': message.message}

  return data_formatting(data=output)
