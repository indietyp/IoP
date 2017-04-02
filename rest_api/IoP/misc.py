from IoP import app

from uuid import UUID
from flask import request
from copy import deepcopy
from models.plant import Plant
from models.mesh import MeshObject
from IoP.tooling import data_formatting
from models.context import DayNightTime
from mesh_network.daemon import MeshNetwork
from playhouse.shortcuts import model_to_dict
from mesh_network.dedicated import MeshDedicatedDispatch


@app.route('/discover', methods=['GET', 'PUT'])
def discover():
  # GET: select:
  # GET: dict: Boolean
  # GET: registered: Boolean
  if request.method == 'GET':
    mode = request.args.get('dict', '').lower()
    selected = request.args.get('select', '').lower()
    registered = request.args.get('registered', '').lower()

    if selected in ['', 'default']:
      selected = 'normal'
    selectable = ['minimal', 'normal', 'detailed', 'extensive']
    mode = True if mode == 'true' else False
    registered = True if registered == 'true' else False

    meshobjects = MeshObject.filter(registered=registered)

    if selected not in selectable:
      return data_formatting(400)

    output = []
    for meshobject in list(meshobjects):
      used = []
      if selected in selectable:
        used.append('ip')

      if selected in selectable[1:]:
        used.append('master')

      if selected in selectable[2:]:
        used.append('registered')

      if selected in selectable[3:]:
        used.append('created_at')

      data = [] if not mode else {}
      for use in used:
        if isinstance(meshobject[use], UUID):
          meshobject[use] = str(meshobject[use])

        if not mode:
          data.append(meshobject[use])
        else:
          data[use] = meshobject[use]
      output.append(data)

    return data_formatting(data=output)

  else:
    MeshNetwork().discover(1)
    return data_formatting()


@app.route('/day/night', methods=['GET', 'POST'])
def day_night():
  # GET: select:
  # GET: dict: Boolean
  # GET: registered: Boolean

  if request.method == 'GET':
    output = []

    for daynight in DayNightTime.select():
      dn = model_to_dict(daynight)
      dn['uuid'] = str(dn['uuid'])
      output.append(dn)

    return data_formatting(data=output)

  else:
    data = deepcopy(request.form)
    for day_night in DayNightTime.select():
      day_night.stop = data['stop']
      day_night.start = data['start']
      day_night.ledbar = data['ledbar']
      day_night.display = data['display']
      day_night.generalleds = data['generalleds']
      day_night.notification = data['notification']
      day_night.save()

    for slave in list(Plant.select().where(Plant.role != 'master')):
      information = {'min': data['start'], 'max': data['stop']}
      MeshDedicatedDispatch().slave_update(0, information, slave)

    MeshDedicatedDispatch().update('day night time', DayNightTime.select()[0].uuid)

    return data_formatting()


@app.route('/host', methods=['GET', 'POST'])
def host():
  if request.method == 'GET':
    plant = Plant.get(host=True)

    output = model_to_dict(plant)
    del output['created_at']

    return data_formatting(data=output)
  else:
    local = Plant.get(localhost=True)

    if not local.host:
      host = Plant.get(host=True)
      host.host = False
      host.save()

      local.host = True
      local.save()

      MeshDedicatedDispatch().update('host', local.uuid)

    return data_formatting()
