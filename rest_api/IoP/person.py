from IoP import app

from uuid import UUID
from flask import request
from models.plant import Person
from IoP.tooling import data_formatting, get_data
from IoP.config import PERSONS_GET, PERSONS_PUT, PERSON_GET, PERSON_POST
from playhouse.shortcuts import model_to_dict
from mesh_network.dedicated import MeshDedicatedDispatch


@app.route('/persons', methods=['GET', 'PUT'])
# @app.route('/responsibles', methods=['GET', 'PUT'])
def persons():
  # GET: select: minimal, normal, detailed, extensive, default (normal)
  # GET: dict: Boolean

  if request.method == 'GET':
    data, code = get_data(required=PERSONS_GET, restrictive=True, hardmode=True)
    if code == 400:
      return data_formatting(400)

    mode = data['dict']
    selector = data['select']
    persons = Person.select().dicts()
    selectable = ['minimal', 'normal', 'detailed', 'extensive']
    collection = {}

    for selected in selector:
      output = []

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

      if len(selector) > 1:
        collection[selected] = output

    if len(collection.keys()) != 0:
      output = collection
    return data_formatting(data=output)

  else:
    data, code = get_data(required=PERSONS_PUT, restrictive=True, hardmode=True)
    if code == 400:
      return data_formatting(400)

    person = Person()

    person.name = data['name']
    person.email = data['email']

    person.wizard = data['wizard']

    if data['wizard']:
      wizards = Person.filter(wizard=True)
      for old in wizards:
        old.wizard = False
        old.save()

    person.save()
    return data_formatting()


@app.route('/persons/<r_uuid>', methods=['GET', 'POST', 'DELETE'])
# @app.route('/responsibles/<r_uuid>', methods=['GET', 'POST', 'DELETE'])
def person(r_uuid):
  # GET: select: full, default (full)
  # POST: replaceable: email, name, wizard
  # DELETE
  person = Person.get(uuid=r_uuid)

  if request.method == 'GET':
    data, code = get_data(required=PERSON_GET, restrictive=True, hardmode=True)
    if code == 400:
      return data_formatting(400)

    selector = data['select']
    collection = {}

    for selected in selector:
      if selected == 'full':
        output = model_to_dict(person)
        del output['id']
        del output['preset']
        output['uuid'] = str(output['uuid'])

      if len(selector) > 1:
        collection[selected] = output

    if len(collection.keys()) != 0:
      output = collection

    return data_formatting(data=output)

  elif request.method == 'POST':
    data, code = get_data(required=PERSON_POST, restrictive=True)
    if code == 400:
      return data_formatting(400)

    if data['name'] != '':
      person.name = data['name']

    if data['email'] != '':
      person.email = data['email']

    if data['wizard'] is not None:

      if data['wizard']:
        wizards = Person.filter(wizard=True)

        for old in wizards:
          old.wizard = False
          old.save()
      person.wizard = data['wizard']

    person.save()
    MeshDedicatedDispatch().update('person', person.uuid)
    return data_formatting()

  else:
    if Person.select().where(Person.uuid == r_uuid).count() > 0:
      Person.get(uuid=r_uuid).delete_instance()
    else:
      return data_formatting(304)

    return data_formatting()
