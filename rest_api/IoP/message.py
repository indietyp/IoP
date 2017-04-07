from IoP import app

from uuid import UUID
from copy import deepcopy
from flask import request
from IoP.tooling import data_formatting, get_data
from IoP.config import MESSAGES_GET, MESSAGES_PUT, MESSAGE_GET, MESSAGE_POST
from playhouse.shortcuts import model_to_dict
from models.plant import Plant, MessagePreset
from mesh_network.dedicated import MeshDedicatedDispatch


@app.route('/messages', methods=['GET', 'PUT'])
def messages():

  if request.method == 'GET':
    # GET: select: minimal, normal, detailed, extensive, default (normal)
    # GET: dict: Boolean
    data, code = get_data(required=MESSAGES_GET, restrictive=True, hardmode=True)
    if code == 400:
      return data_formatting(400)

    mode = data['dict']
    selector = data['select']
    selectable = ['minimal', 'normal', 'detailed', 'extensive']

    messages = MessagePreset.select().dicts()
    collection = {}

    for selected in selector:
      output = []

      for message in list(messages):
        used = []
        if selected in selectable:
          used.append('uuid')

        if selected in selectable[1:]:
          used.append('name')

        if selected in selectable[2:]:
          used.append('created_at')

        if selected in selectable[3:]:
          used.append('message')

        data = [] if not mode else {}
        for use in used:
          if isinstance(message[use], UUID):
            message[use] = str(message[use])

          if not mode:
            data.append(message[use])
          else:
            data[use] = message[use]
        output.append(data)

      if len(selector) > 1:
        collection[selected] = output

    if len(collection.keys()) != 0:
      output = collection

    return data_formatting(data=output)
  else:
    data, code = get_data(required=MESSAGES_PUT, restrictive=True)
    if code == 400:
      return data_formatting(400)

    for message in MessagePreset.select():
      if message.name == data['heading']:
        return data_formatting(304)

    msg = MessagePreset()
    msg.name = data['heading']
    msg.message = data['message']
    msg.save()

    return data_formatting()


@app.route('/messages/<m_uuid>', methods=['GET', 'POST'])
def message(m_uuid):
  # GET: select: message, full, default (full)
  if request.method == 'GET':
    message = MessagePreset.get(uuid=m_uuid)
    data, code = get_data(required=MESSAGE_GET, restrictive=True, hardmode=True)
    if code == 400:
      return data_formatting(400)
    selector = data['select']
    collection = {}

    for selected in selector:
      if selected == 'full':
        output = model_to_dict(message)
        del output['id']
        del output['created_at']
        output['uuid'] = str(output['uuid'])
      else:
        output = {'message': message.message}

      if len(selector) > 1:
        collection[selected] = output

    if len(collection.keys()) != 0:
      output = collection
    return data_formatting(data=output)

  else:
    data, code = get_data(required=MESSAGE_POST, restrictive=True)
    if code == 400:
      return data_formatting(400)

    preset, _ = MessagePreset.get_or_create(name=data['heading'],
                                            defaults={'message': data['message']})
    preset.message = data['message']
    preset.save()

    if data['person']:
      plant = Plant.get(uuid=data['plant'])
      plant.person.preset = preset
      plant.person.save()

    MeshDedicatedDispatch().update('message', preset.uuid)
    return data_formatting()
