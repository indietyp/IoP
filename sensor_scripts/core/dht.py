import sys
import Adafruit_DHT

from pymongo import MongoClient

from ...tools.main import Tools
from ..extensions.mailer import PlantMailer
from ..extensions.led.general import generalStatus

class DHT22():
  """docstring for DHT22"""
  def __init__(self):
    # super(DHT22, self).__init__()
    # self.arg = arg
    client = MongoClient
    self.db = client.iop

  def get_data(self):
    plant_id = self.db.Plant.find_one({'localhost': True})['plant_id']

    # PARSE PARAMETERS
    rawSensor = self.db.Sensor.find_one({'t': 'temperature'})['m']
    sensor = Adafruit_DHT.DHT22 if rawSensor == 'DHT22' else Adafruit_DHT11
    pin = self.db.ExternalDevices.find_one({'n': 'DHT22'})['p']['gpio']

    # FETCH DATA FROM SENSOR
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    if humidity is not None and temperature is not None:
      t_id = self.db.Sensor.find_one({'t': 'temperature'})['s_id']
      h_id = self.db.Sensor.find_one({'t': 'humidity'})['s_id']
      # INSERT IN DATABASE
      tool_chain = Tools(self.db, plant_id)
      tool_chain.insertSensor(t_id, round(temperature, 2))
      tool_chain.insertSensor(h_id, round(humidity, 2))

      # ACTIVATE MAILER
      PlantMailer(plant_id, t_id).send()
      PlantMailer(plant_id, h_id).send()

      # INSERT DATA IN GENERAL STATUS LEDS
      general_status(plant_id, t_id, round(temperature,2)).insert()
      general_status(plant_id, h_id, round(humidity,2)).insert().set()

      return tool_chain.change_detector()

    else:
      return -1
      # sys.exit(1)
