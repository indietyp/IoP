import sys
import Adafruit_DHT

from pymongo import MongoClient

from ..tools.main import Tools
from ..extensions.mailer import PlantMailer
from ..extensions.led.general import generalStatus

client = MongoClient()
db = client.pot

plantAbbreviation = db.Plant.find_one({'localhost': True})['abbreviation']

# PARSE PARAMETERS
rawSensor = db.SensorType.find_one({'t': 'temperature'})['m']
sensor = Adafruit_DHT.DHT22 if rawSensor == 'DHT22' else Adafruit_DHT11
pin = db.ExternalDevices.find_one({'n': 'DHT22'})['p']['gpio']

# FETCH DATA FROM SENSOR
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

print 'test'
if humidity is not None and temperature is not None:

  print humidity
  print temperature

  # INSERT IN DATABASE
  toolChain = Tools(db, plantAbbreviation)
  toolChain.insertSensor('t', round(temperature, 2))
  toolChain.insertSensor('h', round(humidity, 2))

  # ACTIVATE MAILER
  mailerTemperature = PlantMailer('m','t')
  mailerTemperature.send()

  mailerHumidity = PlantMailer('m','h')
  mailerHumidity.send()

  # INSERT DATA IN GENERAL STATUS LEDS
  generalTemperature = generalStatus('m', 't', round(temperature,2))
  generalTemperature.insert()

  generalHumidity = generalStatus('m', 'h', round(humidity,2))
  generalHumidity.insert()
  generalHumidity.set()
else:
  sys.exit(1)
