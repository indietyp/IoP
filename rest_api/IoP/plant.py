from IoP import app

import datetime
from uuid import UUID
from flask import request
from models.mesh import MeshObject
from peewee import Clause, fn, SQL
from playhouse.shortcuts import model_to_dict
from mesh_network.dedicated import MeshDedicatedDispatch
from models.plant import Person, Plant, PlantNetworkUptime, PlantNetworkStatus
from IoP.tooling import get_sensor_data_high_low, copy_model_instance_from_localhost, data_formatting, time_request_from_converter, get_data
from IoP.config import PLANTS_GET, PLANTS_PUT, PLANT_GET, PLANT_POST, PLANT_SENSORS_GET, PLANT_SENSOR_GET, PLANT_RESPONSIBLE_GET, PLANT_RESPONSIBLE_POST, PLANT_MESSAGE_GET, PLANT_STATUS_GET
from models.sensor import Sensor, SensorData, SensorDataPrediction, SensorSatisfactionValue, SensorSatisfactionLevel, SensorCount, SensorStatus
slave_supported = ['moisture']


@app.route('/plants', methods=['GET', 'PUT'])
def plants():
  # GET: select: minimal, normal, detailed, extensive, master, satisfaction, default (normal)
  # GET: dict: Boolean
  if request.method == 'GET':
    data, code = get_data(required=PLANTS_GET, restrictive=True, hardmode=True)
    if code == 400:
      return data_formatting(400)

    selector = data['select']
    mode = data['dict']
    root_plants = Plant.select().dicts()
    collection = {}

    for selected in selector:
      plants = root_plants.where(Plant.role == 'master') if selected == 'master' else root_plants
      plants = list(plants)

      output = []
      if selected not in ['satisfaction', 'sensorsatisfaction']:
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

      elif selected in ['satisfaction', 'sensorsatisfaction']:
        output = {}
        sensors = Sensor.select()
        for plant in plants:
          host = None
          if plant['role'] != 'master':
            host = Plant.get(Plant.uuid == plant['role'])

          if selected == 'satisfaction':
            statuses = []
          else:
            output[str(plant['uuid'])] = {}

          for sensor in sensors:
            target = Plant.get(uuid=plant['uuid'])
            if sensor.name not in slave_supported and host is not None:
              target = host

            status = SensorStatus.get(SensorStatus.sensor == sensor, SensorStatus.plant == target)
            if selected == 'satisfaction':
              inserted = 1
              if status.level.label == 'threat':
                inserted = 3
              elif status.level.label == 'cautioning':
                inserted = 2
              statuses.append(inserted)
            else:
              if status.level.label not in output[str(plant['uuid'])]:
                output[str(plant['uuid'])][status.level.label] = []

              output[str(plant['uuid'])][status.level.label].append({'name': sensor.name, 'uuid': str(sensor.uuid)})

          if selected == 'satisfaction':
            maximum = max(statuses)
            label = 'optimum'
            if maximum == 3:
              label = 'threat'
            elif maximum == 2:
              label = 'cautioning'

            output[str(plant['uuid'])] = {'streak': plant['sat_streak'], 'name': label}

      if len(selector) > 1:
        collection[selected] = output

    if len(collection.keys()) != 0:
      output = collection

    return data_formatting(data=output)
  else:
    # PUT: register: true
    data, code = get_data(required=PLANTS_PUT, restrictive=True)
    if code == 400:
      return data_formatting(400)
    register = data['register']

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

    if data['uuid'] != '':
      plant.uuid = data['uuid']
    if data['persistant_hold'] != '':
      plant.persistant_hold = data['persistant_hold']

    if not discovered.master:
      if data['role'] == '':
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
    data, code = get_data(required=PLANT_GET, restrictive=True, hardmode=True)
    if code == 400:
      return data_formatting(400)

    collection = {}
    selector = data['select']

    for selected in selector:
      plant = list(Plant.select(Plant, fn.CAST(Clause(fn.strftime('%s', Plant.created_at), SQL('AS INT'))).alias('created_at'))
                        .where(Plant.uuid == p_uuid).dicts())[0]
      plant['uuid'] = str(plant['uuid'])

      if selected not in ['full', 'intervals', 'survived']:
        output = {selected: plant[selected]}
      elif selected in ['intervals']:
        output = {'connection_lost': plant['connection_lost'],
                  'non_persistant': int(plant['persistant_hold'] * 5 / 60 / 24),
                  'notification': plant['interval']}
      elif selected in ['survived']:
        difference = datetime.datetime.now() - datetime.datetime.fromtimestamp(plant['created_at'])
        output = float(difference.days + round((difference.seconds // 3600) / 24, 1))
      else:
        output = plant

      if len(selector) > 1:
        collection[selected] = output

    if len(collection.keys()) != 0:
      output = collection

    return data_formatting(data=output)
  elif request.method == 'POST':
    # POST: replace: name, type, location, ranges, responsible
    # POST: mode: add, reset, online, offline
    # POST: new: DATA
    data, code = get_data(required=PLANT_POST, restrictive=True)
    if code == 400:
      return data_formatting(400)

    keys = list(data.keys())

    if data['mode'] == '':
      mode = 'add' if 'satisfaction' in keys else 'offline'
    else:
      mode = data['mode'].lower()

    plant = Plant.get(uuid=p_uuid)

    if data['name'] != '':
      plant.name = data['name']

    if data['species'] != '':
      plant.species = data['species']

    if data['location'] != '':
      plant.location = data['location']

    if data['ranges']:
      try:
        sensor = Sensor.get(name=data['sensor'])
      except Exception:
        try:
          sensor = Sensor.get(uuid=data['sensor'])
        except Exception:
          return data_formatting(400)

      level_yellow = SensorSatisfactionLevel.get(SensorSatisfactionLevel.name_color == 'yellow')
      level_green = SensorSatisfactionLevel.get(SensorSatisfactionLevel.name_color == 'green')

      value_yellow = SensorSatisfactionValue.get(SensorSatisfactionValue.plant == plant,
                                                 SensorSatisfactionValue.sensor == sensor,
                                                 SensorSatisfactionValue.level == level_yellow)

      value_green = SensorSatisfactionValue.get(SensorSatisfactionValue.plant == plant,
                                                SensorSatisfactionValue.sensor == sensor,
                                                SensorSatisfactionValue.level == level_green)

      value_yellow.min_value = int(request.form.getlist('range[]')[0])
      value_green.min_value = int(request.form.getlist('range[]')[1])
      value_green.max_value = int(request.form.getlist('range[]')[2])
      value_yellow.max_value = int(request.form.getlist('range[]')[3])

      value_green.save()
      value_yellow.save()

      MeshDedicatedDispatch().update('plant satisfaction level', plant.uuid)
      if sensor.name == 'moisture' and plant.role != 'master':
        # logger.info('executing slave update')
        information = {'min': value_yellow.min_value, 'max': value_yellow.max_value}
        MeshDedicatedDispatch().slave_update(2, information, plant)

    if data['responsible']:
      person = Person.get(email=data['email'], name=data['firstname'])
      plant.person = person
      plant.save()

    if data['satisfaction']:
      if mode == 'add':
        plant.sat_streak += 1
      else:
        plant.sat_streak = 1

    if data['alive']:
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

    if data['notification']:
      _, _, hours = time_request_from_converter(data)
      plant.interval = int(round(hours))

    if data['connection-lost']:
      _, minutes, _ = time_request_from_converter(data)
      plant.connection_lost = int(round(minutes))

    if data['non-persistant']:
      _, minutes, _ = time_request_from_converter(data)
      plant.persistant_hold = int(round(minutes / 5))

    plant.save()
    MeshDedicatedDispatch().update('plant', plant.uuid)
    return data_formatting()


@app.route('/plants/<p_uuid>/sensor', methods=['GET'])
def plant_sensors(p_uuid):
  # GET: select: range (default), default
  plant = Plant.get(uuid=p_uuid)
  data, code = get_data(required=PLANT_SENSORS_GET, restrictive=True, hardmode=True)
  if code == 400:
    return data_formatting(400)

  selector = data['select']
  collection = {}

  for selected in selector:
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
        output.append({'settings': tmp, 'sensor': sensor.name, 'uuid': str(sensor.uuid)})

    if len(selector) > 1:
        collection[selected] = output

  if len(collection.keys()) != 0:
    output = collection

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
  plant = Plant.get(uuid=p_uuid)
  try:
    sensor = Sensor.get(uuid=s_uuid)
  except Exception:
    sensor = Sensor.get(name=s_uuid)

  if plant.role != 'master' and sensor.name not in slave_supported:
    plant = Plant.get(uuid=plant.role)

  data, code = get_data(required=PLANT_SENSOR_GET, restrictive=True)
  if code == 400:
    return data_formatting(400)

  selector = data['select']
  maximum = data['max']
  backlog = data['backlog']
  start = data['start']
  stop = data['stop']
  ever = data['ever']
  collection = {}

  for selected in selector:
    if selected == 'timespan':
      start = datetime.datetime.min if start <= 0 else datetime.datetime.fromtimestamp(start)
      stop = datetime.datetime.max if stop >= 253402297200 else datetime.datetime.fromtimestamp(stop)

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
      data = data.where(SensorData.created_at > start, SensorData.created_at < stop)
      output = list(data)
    else:
      data = data.order_by(SensorData.created_at.desc()).offset(start).limit(stop - start)
      output = list(data)

    if len(selector) > 1:
      collection[selected] = output

  if len(collection.keys()) != 0:
    output = collection

  return data_formatting(data=output)


@app.route('/plants/<p_uuid>/responsible', methods=['GET', 'POST'])
def plant_responsible(p_uuid):
  # GET: select: email, wizard, username, full, default (full)
  responsible = Plant.get(uuid=p_uuid).person
  if request.method == 'GET':
    responsible = model_to_dict(responsible)
    responsible['uuid'] = str(responsible['uuid'])

    data, code = get_data(required=PLANT_RESPONSIBLE_GET, restrictive=True)
    if code == 400:
      return data_formatting(400)
    selector = data['select']
    collection = {}

    for selected in selector:
      if selected != 'full':
        used = [selected, 'uuid']
      else:
        used = list(responsible.keys())

      output = {}

      for key in used:
        if key not in ['id', 'preset']:
          output[key] = responsible[key]

      if len(selector) > 1:
        collection[selected] = output

    if len(collection.keys()) != 0:
      output = collection

    return data_formatting(data=output)
  else:
    data, code = get_data(required=PLANT_RESPONSIBLE_POST, restrictive=True)
    if code == 400:
      return data_formatting(400)

    if data['email'] != '' and data['name'] != '':
      responsible = Person.get(Person.email ** data['email'], Person.name ** data['name'])
    elif data['uuid'] != '':
      responsible = Person.get(uuid=data['uuid'])

    plant = Plant.get(uuid=p_uuid)
    plant.person = responsible
    plant.save()

    return data_formatting()


@app.route('/plants/<p_uuid>/status', methods=['GET'])
def plant_status(p_uuid):
  # GET: select: average, online
  plant = Plant.get(uuid=p_uuid)
  data, code = get_data(required=PLANT_STATUS_GET, restrictive=True)
  if code == 400:
    return data_formatting(400)
  selector = data['select']
  collection = {}

  for selected in selector:
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

    if len(selector) > 1:
      collection[selected] = output

  if len(collection.keys()) != 0:
    output = collection

  return data_formatting(data=output)


@app.route('/plants/<p_uuid>/message', methods=['GET'])
def plant_message(p_uuid):
  # GET: select: full
  plant = Plant.get(uuid=p_uuid)
  data, code = get_data(required=PLANT_MESSAGE_GET, restrictive=True)
  if code == 400:
    return data_formatting(400)
  selector = data['select']
  collection = {}

  for selected in selector:
    if selected == 'full':
      message = plant.person.preset
      output = {'uuid': str(message.uuid), 'message': message.message}

    if len(selector) > 1:
      collection[selected] = output

  if len(collection.keys()) != 0:
    output = collection

  return data_formatting(data=output)
