from IoP import app

from uuid import UUID
from copy import deepcopy
from flask import request
from IoP.tooling import data_formatting
from playhouse.shortcuts import model_to_dict
from models.plant import Plant, MessagePreset
from mesh_network.dedicated import MeshDedicatedDispatch


@app.route('/messages', methods=['GET', 'PUT'])
def messages():

  if request.method == 'GET':
    # GET: select: minimal, normal, detailed, extensive, default (normal)
    # GET: dict: Boolean
    mode = request.args.get('dict', '').lower()
    selected = request.args.get('select', '').lower()
    if selected in ['', 'default']:
      selected = 'normal'
    selectable = ['minimal', 'normal', 'detailed', 'extensive']

    messages = MessagePreset.select()
    mode = True if mode == 'true' else False
    output = []

    if selected not in selectable:
      return data_formatting(400)

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

    return data_formatting(data=output)
  else:
    data = deepcopy(request.form)
    data['heading'] = data['heading'].lower()

    for message in MessagePreset.select():
      if message.name == data['heading']:
        return {'info': 'failed, not unique'}

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
    selected = request.args.get('select', '').lower()
    if selected in ['', 'default']:
      selected = 'full'
    selectable = ['message', 'full']

    if selected not in selectable:
      return data_formatting(400)

    if selected == 'full':
      output = model_to_dict(message)
      del output['id']
      del output['created_at']
      output['uuid'] = str(output['uuid'])
    else:
      output = {'message': message.message}

    return data_formatting(data=output)

  else:
    data = deepcopy(request.form)
    preset, _ = MessagePreset.get_or_create(name=data['heading'],
                                            defaults={'message': data['message']})
    preset.message = data['message']
    preset.save()

    if data['responsible'] is True:
      plant = Plant.get(uuid=data['plant'])
      plant.person.preset = preset
      plant.person.save()

    MeshDedicatedDispatch().update('message', preset.uuid)
    return data_formatting()
