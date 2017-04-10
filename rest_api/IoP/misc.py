from IoP import app

import datetime
from uuid import UUID
from flask import request
from models.plant import Plant
from models.mesh import MeshObject
from IoP.tooling import data_formatting, get_data
from IoP.config import DISCOVER_GET, DISCOVER_POST, DAYNIGHT_GET, DAYNIGHT_POST, HOST_GET
from models.context import DayNightTime
from mesh_network.daemon import MeshNetwork
from playhouse.shortcuts import model_to_dict
from mesh_network.dedicated import MeshDedicatedDispatch


@app.route('/discover', methods=['GET', 'PUT'])
def discover():
  # GET: select:
  # GET: dict: Boolean
  if request.method == 'GET':
    data, code = get_data(required=DISCOVER_GET, restrictive=True, hardmode=True)
    if code == 400:
      return data_formatting(400)

    mode = data['dict']
    selector = data['select']
    registered = data['registered']
    selectable = ['minimal', 'normal', 'detailed', 'extensive']
    collection = {}

    if registered is not None:
      meshobjects = MeshObject.filter(registered=registered).dicts()
    else:
      meshobjects = MeshObject.select().dicts()

    for selected in selector:
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

          if isinstance(meshobject[use], datetime.datetime):
            meshobject[use] = meshobject[use].timestamp()

          if not mode:
            data.append(meshobject[use])
          else:
            data[use] = meshobject[use]
        output.append(data)

      if len(selector) > 1:
        collection[selected] = output

    if len(collection.keys()) != 0:
      output = collection

    return data_formatting(data=output)

  else:
    data, code = get_data(required=DISCOVER_POST, restrictive=True)
    if code == 400:
      return data_formatting(400)

    if data['execute']:
      MeshNetwork().discover(1)

    return data_formatting()


@app.route('/daynight', methods=['GET', 'POST'])
def day_night():
  if request.method == 'GET':
    data, code = get_data(required=DAYNIGHT_GET, restrictive=True, hardmode=True)
    if code == 400:
      return data_formatting(400)
    selector = data['select']
    collection = {}

    for selected in selector:
      output = []

      if selected == 'full':
        for daynight in DayNightTime.select():
          dn = model_to_dict(daynight)
          dn['uuid'] = str(dn['uuid'])
          output.append(dn)

      if len(selector) > 1:
        collection[selected] = output

    if len(collection.keys()) != 0:
      output = collection
    return data_formatting(data=output)

  else:
    data, code = get_data(required=DAYNIGHT_POST, restrictive=True)
    if code == 400:
      return data_formatting(400)

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
    data, code = get_data(required=HOST_GET, restrictive=True, hardmode=True)
    if code == 400:
      return data_formatting(400)
    selector = data['select']
    print('Host: {}'.format(str(selector)))
    collection = {}

    # output = {}
    for selected in selector:
      output = []
      if selected == 'full':
        output = model_to_dict(plant)
        output['timestamp'] = output['created_at'].timestamp()
        output['uuid'] = str(output['uuid'])

        del output['id']
        del output['person']
        del output['created_at']

      if len(selector) > 1:
        collection[selected] = output

    if len(collection.keys()) != 0:
      output = collection
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
