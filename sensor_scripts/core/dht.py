import sys
import random
import Adafruit_DHT

# from pymongo import MongoClient
from models.plant import Plant
from models.sensor import Sensor
from tools.sensor import ToolChainSensor
# from tools.mail import ToolChainMailing
# from ...tools.main import Tools
# from ...tools.mailer import Mailer
# from ..extensions.led.general import generalStatus


class DHT22:
  """readout for DHT22/11 sensor"""

  def __init__(self):
    pass

  @staticmethod
  def run():
    # == needs to be there 'is' is not valid!
    plant = Plant.select().where(Plant.localhost == True)[0]

    # PARSE PARAMETERS
    temperature = {'sensor': Sensor.select().where(Sensor.name == 'temperature')[0],
                   'plant': plant}
    humidity = {'sensor': Sensor.select().where(Sensor.name == 'humidity')[0],
                'plant': plant}

    if temperature['sensor'].model == humidity['sensor'].model:
      sensor = Adafruit_DHT.DHT22 if temperature['sensor'].model == 'DHT22' else Adafruit_DHT.DHT11
    pin = 18

    # FETCH DATA FROM SENSOR
    humidity['value'], temperature['value'] = Adafruit_DHT.read_retry(sensor, pin)
    print(humidity)
    print(temperature)
    if humidity is not None and temperature is not None:
      # print(str(temperature))
      pass
      # print(str(humidity))
      # temperature = round(temperature, 2)
      # humidity = round(humidity, 2)

      tools = ToolChainSensor()

      print('temp ' + str(tools.insert_data(temperature)))
      # print('humi ' + str(tools.insert_data(humidity)))

      # tools.set_hardware(temperature)
      # tools.set_hardware(humidity)

    # else:
    #   return -1

if __name__ == '__main__':
  DHT22.run()
