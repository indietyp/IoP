from IoP import app

from uuid import UUID
from flask import request
from models.plant import Person
from IoP.tooling import data_formatting
from playhouse.shortcuts import model_to_dict
from mesh_network.dedicated import MeshDedicatedDispatch


@app.route('/persons', methods=['GET', 'PUT'])
@app.route('/responsibles', methods=['GET', 'PUT'])
def persons():
  # GET: select: minimal, normal, detailed, extensive, default (normal)
  # GET: dict: Boolean

  if request.method == 'GET':
    mode = request.args.get('dict', '').lower()
    selected = request.args.get('select', '').lower()
    if selected in ['', 'default']:
      selected = 'detailed'
    selectable = ['minimal', 'normal', 'detailed', 'extensive']

    persons = Person.select()
    mode = True if mode == 'true' else False
    output = []

    if selected not in selectable:
      return data_formatting(400)

    for person in list(persons):
      used = []
      if selected in selectable:
        used.append('uuid')

      if selected in selectable[1:]:
        used.append('name')

      if selected in selectable[2:]:
        used.append('email')

      if selected in selectable[3:]:
        used.append('wizard')

      data = [] if not mode else {}
      for use in used:
        if isinstance(person[use], UUID):
          person[use] = str(person[use])

        if not mode:
          data.append(person[use])
        else:
          data[use] = person[use]
      output.append(data)

    return data_formatting(data=output)

  else:
    person = Person()

    person.name = request.form['name'].lower()
    person.email = request.form['email'].lower()
    person.wizard = True if request.form['wizard'].lower() == 'true' else False

    person.save()
    return data_formatting()


@app.route('/persons/<r_uuid>', methods=['GET', 'POST', 'DELETE'])
@app.route('/responsibles/<r_uuid>', methods=['GET', 'POST', 'DELETE'])
def person(r_uuid):
  # GET: select: full, default (full)
  # POST: replaceable: email, name, wizard
  # DELETE

  person = Person.get(uuid=r_uuid)
  if request.method == 'GET':
    selected = request.args.get('select', '').lower()
    if selected in ['', 'default']:
      selected = 'detailed'
    selectable = ['full']

    if selected not in selectable:
      return data_formatting(400)

    output = model_to_dict(person)
    del output['id']
    del output['preset']
    output['uuid'] = str(output['uuid'])

    return data_formatting(data=output)

  elif request.method == 'POST':
    replaceable = ['name', 'email', 'wizard']
    data = [x.lower() for x in request.form]
    keys = list(data.keys())

    if len(set(keys) - set(replaceable)):
      return data_formatting(400)

    if 'name' in keys:
      person.name = data['name']

    if 'email' in keys:
      person.email = data['email']

    if 'wizard' in keys:
      wizards = Person.filter(wizard=True)
      data['wizard'] = True if data['wizard'] == 'true' else False

      for old in wizards:
        old.wizard = False
        old.save()

      person.wizard = True

    person.save()
    MeshDedicatedDispatch().update('person', person.uuid)
    return data_formatting()

  else:
    if Person.select().where(Person.uuid == r_uuid).count() > 0:
      Person.get(uuid=r_uuid).delete_instance()
    else:
      return data_formatting(304)

    return data_formatting()
