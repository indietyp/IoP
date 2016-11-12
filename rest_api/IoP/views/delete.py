import json
from IoP import app
from uuid import UUID
from models.plant import Person


@app.route('/delete/responsible/<r_uuid>')
def delete_responsible(r_uuid):
  if Person.select().where(Person.uuid == UUID(r_uuid)).count() > 0:
    Person.get(uuid=UUID(r_uuid)).delete_instance()
  else:
    return json.dumps({'info': 'no person with this UUID'})

  return json.dumps({'info': 'success'})
