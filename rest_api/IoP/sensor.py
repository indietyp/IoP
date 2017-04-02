from IoP import app

from uuid import UUID
from flask import request
from models.sensor import Sensor
from IoP.tooling import data_formatting
from playhouse.shortcuts import model_to_dict


@app.route('/sensors', methods=['GET'])
def sensors():
  # GET: select: minimal, normal, detailed, extensive, default (normal)
  # GET: dict: Boolean
  mode = request.args.get('dict', '').lower()
  selected = request.args.get('select', '').lower()
  if selected in ['', 'default']:
    selected = 'normal'
  selectable = ['minimal', 'normal', 'detailed', 'extensive']

  sensors = Sensor.select()
  mode = True if mode == 'true' else False
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

    data = [] if not mode else {}
    for use in used:
      if isinstance(sensor[use], UUID):
        sensor[use] = str(sensor[use])

      if not mode:
        data.append(sensor[use])
      else:
        data[use] = sensor[use]
    output.append(data)

  return data_formatting(data=output)


@app.route('/sensors/<s_uuid>', methods=['GET'])
def sensor(s_uuid):
  # GET: select: range, unit, full, default (full)

  try:
    sensor = Sensor.get(uuid=s_uuid)
  except:
    sensor = Sensor.get(name=s_uuid)
  selected = request.args.get('select', '').lower()
  selectable = ['range', 'unit', 'full']

  if selected in ['', 'default']:
    selected = 'full'

  if selected in selectable:
    return data_formatting(400)

  if selected != 'full':
    output = model_to_dict(sensor)
    del output['id']

    return data_formatting(data=output)
  else:
    output = model_to_dict(sensor)[selected]
    return data_formatting(data=output)
