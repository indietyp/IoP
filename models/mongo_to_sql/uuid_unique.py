from models.sensor import SensorSatisfactionValue
import uuid

for person in SensorSatisfactionValue.select():
  person.uuid = uuid.uuid4()
  person.save()
