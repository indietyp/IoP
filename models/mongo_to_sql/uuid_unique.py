from models.plant import Person
import uuid

for person in Person.select():
  person.uuid = uuid.uuid4()
  person.save()
