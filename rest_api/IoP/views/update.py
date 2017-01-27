from IoP import app
from flask import request
import json
from copy import deepcopy

# UPDATE
# PLANT:
# - NAME
# - RESPONSIBLE
# - RANGE
# -- GREEN
# -- YELLOW
# - LOCATION
# - TYPE
from models.plant import Plant, Person
from models.plant import PlantNetworkStatus, PlantNetworkUptime
from models.sensor import SensorSatisfactionValue, SensorSatisfactionLevel, Sensor
from models.plant import MessagePreset
from models.context import DayNightTime
from mesh_network.dedicated import MeshDedicatedDispatch


@app.route('/update/plant/<p_uuid>/name', methods=['POST'])
def update_plant_name(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.name = request.form['new'].lower()
  plant.save()

  MeshDedicatedDispatch().update('plant', plant.uuid)
  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/type', methods=['POST'])
def update_plant_type(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.species = request.form['new'].lower()
  plant.save()

  MeshDedicatedDispatch().update('plant', plant.uuid)
  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/location', methods=['POST'])
def update_plant_location(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.location = request.form['new'].lower()
  plant.save()

  MeshDedicatedDispatch().update('plant', plant.uuid)
  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/ranges', methods=['POST'])
def update_plant_ranges(p_uuid):
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

  MeshDedicatedDispatch().update('plant', plant.uuid)
  return json.dumps({'info': 'success'})


@app.route('/update/plant/<p_uuid>/responsible', methods=['POST'])
def update_plant_responsible(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  person = Person.get(Person.email == request.form['email'], Person.name == request.form['name'])

  plant.person = person
  plant.save()

  MeshDedicatedDispatch().update('plant', plant.uuid)
  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/satisfaction/level/reset', methods=['POST'])
def update_plant_satisfaction_level_reset(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.sat_streak = 1
  plant.save()

  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/satisfaction/level/add', methods=['POST'])
def update_plant_satisfaction_level_add(p_uuid):
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.sat_streak = plant.sat_streak + 1
  plant.save()
  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/alive/<any(online,offline):mode>/add', methods=['POST'])
def plant_alive_online_offline(p_uuid, mode):
  counterpart = 'online' if mode == 'offline' else 'offline'
  status = PlantNetworkStatus.get(name=mode)
  counterpart = PlantNetworkStatus.get(name=counterpart)

  plant = Plant.get(uuid=p_uuid)
  if plant.role == 'master':
    return json.dumps({'info': 0})

  status = PlantNetworkUptime.get(plant=plant, status=status)
  counterpart = PlantNetworkUptime.get(plant=plant, status=counterpart)

  if counterpart.current != 0:
    counterpart.current = 0
    counterpart.save()

  status.current += 1
  status.overall += 1
  status.save()

  return json.dumps({'info': 1})


def time_request_from_converter(data):
  data = deepcopy(data)

  seconds = 0
  if 'seconds' in data:
    seconds += int(data['seconds'])

  if 'minutes' in data:
    seconds += int(data['minutes']) * 60

  if 'hours' in data:
    seconds += int(data['hours']) * 60 * 60

  if 'days' in data:
    seconds += int(data['days']) * 24 * 60 * 60

  minutes = seconds / 60
  hours = minutes / 60

  return seconds, minutes, hours


@app.route('/update/plant/<p_uuid>/notification/duration', methods=['POST'])
def update_plant_notification_duration(p_uuid):
  _, _, hours = time_request_from_converter(request.form)
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.interval = int(hours)
  plant.save()

  MeshDedicatedDispatch().update('plant', plant.uuid)
  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/connection-lost/duration', methods=['POST'])
def update_plant_connection_lost(p_uuid):
  _, minutes, _ = time_request_from_converter(request.form)
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.connection_lost = int(minutes)
  plant.save()

  MeshDedicatedDispatch().update('plant', plant.uuid)
  return json.dumps({'info': 1})


@app.route('/update/plant/<p_uuid>/non-persistant/duration', methods=['POST'])
def update_plant_persistant_hold(p_uuid):
  _, minutes, _ = time_request_from_converter(request.form)
  plant = Plant.get(Plant.uuid == p_uuid)
  plant.persistant_hold = minutes / 5
  plant.save()

  MeshDedicatedDispatch().update('plant', plant.uuid)
  return json.dumps({'info': 1})


@app.route('/update/notification/message', methods=['POST'])
def update_notification_message():
  data = request.form
  preset, _ = MessagePreset.get_or_create(name=data['name'],
                                          defaults={'message': data['text']})
  preset.message = data['text']
  preset.save()

  if data['responsible'] is True:
    plant = Plant.get(Plant.uuid == data['plant'])
    plant.person.preset = preset
    plant.person.save()

  MeshDedicatedDispatch().update('message', preset.uuid)
  return json.dumps({'info': 'success'})


@app.route('/update/responsible', methods=['POST'])
def update_responsible():
  person = Person.get(Person.uuid == request.form['uuid'])
  person.name = request.form['name']
  person.email = request.form['email']
  person.save()

  MeshDedicatedDispatch().update('person', person.uuid)
  return json.dumps({'info': 'success'})


@app.route('/update/responsible/wizard', methods=['POST'])
def update_responsible_wizard():
  wizards = Person.select().where(Person.wizard == True)

  for old in wizards:
    old.wizard = False
    old.save()

  person = Person.get(Person.uuid == request.form['replacement'])
  person.wizard = True
  person.save()

  MeshDedicatedDispatch().update('person', person.uuid)
  return json.dumps({'info': 'success'})


# add to mesh?
@app.route('/update/day/night/time', methods=['POST'])
def update_day_night():
  data = deepcopy(request.form)
  for day_night in DayNightTime.select():
    day_night.stop = data['stop']
    day_night.start = data['start']
    day_night.ledbar = data['ledbar']
    day_night.display = data['display']
    day_night.generalleds = data['generalleds']
    day_night.notification = data['notification']
    day_night.save()
  return json.dumps({'info': 'success'})


@app.route('/update/current/host/to/localhost')
def update_current_plant_host():
  local = Plant.get(Plant.localhost == True)
  if not local.host:
    host = Plant.get(Plant.host == True)
    host.host = False
    host.save()
    local.host = True
    local.save()

    MeshDedicatedDispatch().update('host', local.uuid)
  return json.dumps({'info': 'processing'})
