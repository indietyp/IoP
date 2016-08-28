from models.sensor import Sensor
import uuid

for sensor in Sensor.select():
  sensor.uuid = uuid.uuid4()
  sensor.save()
