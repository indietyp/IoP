from IoP import app

from uuid import UUID
from flask import request
from models.sensor import Sensor
from IoP.tooling import data_formatting, get_data
from IoP.config import SENSORS_GET, SENSOR_GET
from playhouse.shortcuts import model_to_dict


@app.route('/sensors', methods=['GET'])
def sensors():
  # GET: select: minimal, normal, detailed, extensive, default (normal)
  # GET: dict: Boolean
  selectable = ['minimal', 'normal', 'detailed', 'extensive']
  data, code = get_data(required=SENSORS_GET, restrictive=True, hardmode=True)
  if code == 400:
    return data_formatting(400)

  mode = data['dict']
  selector = data['select']
  sensors = Sensor.select().dicts()
  collection = {}

  for selected in selector:
    output = []

    if selected not in selectable:
      return data_formatting(400)

    for sensor in list(sensors):
      used = []
      if selected in selectable:
        used.append('uuid')

      if selected in selectable[1:]:
        used.append('name')

      if selected in selectable[2:]:
        used.append('unit')
        used.append('model')

      if selected in selectable[3:]:
        used.append('persistant_offset')
        used.append('min_value')
        used.append('max_value')

      data = [] if not mode else {}
      for use in used:
        if isinstance(sensor[use], UUID):
          sensor[use] = str(sensor[use])

        if not mode:
          data.append(sensor[use])
        else:
          data[use] = sensor[use]
      output.append(data)

    if len(selector) > 1:
      collection[selected] = output

  if len(collection.keys()) != 0:
    output = collection

  return data_formatting(data=output)


@app.route('/sensors/<s_uuid>', methods=['GET'])
def sensor(s_uuid):
  # GET: select: range, unit, full, default (full)
  try:
    sensor = Sensor.get(uuid=s_uuid)
  except Exception:
    sensor = Sensor.get(name=s_uuid)

  data, code = get_data(required=SENSOR_GET, restrictive=True, hardmode=True)
  if code == 400:
    return data_formatting(400)
  selector = data['select']
  collection = {}

  for selected in selector:
    if selected == 'full':
      output = model_to_dict(sensor)
      del output['id']
      output['uuid'] = str(output['uuid'])

    elif selected == 'range':
      output = {'max_value': sensor.max_value, 'min_value': sensor.min_value}

    else:
      output = {selected: model_to_dict(sensor)[selected]}

    if len(selector) > 1:
      collection[selected] = output

  if len(collection.keys()) != 0:
    output = collection
  return data_formatting(data=output)
