import sys
import random
# import Adafruit_DHT

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

    light = {'sensor': Sensor.select().where(Sensor.name == 'light')[0],
             'plant': plant}
    moisture = {'sensor': Sensor.select().where(Sensor.name == 'moisture')[0],
                'plant': plant}

    if temperature['sensor'].model == humidity['sensor'].model:
      pass
      # sensor = Adafruit_DHT.DHT22 if temperature['semsor'].name == 'DHT22' else Adafruit_DHT11
    pin = 18

    humidity['value'], temperature['value'] = random.random() * 100, random.random() * 20 + 10
    light['value'], moisture['value'] = random.random() * 100, random.random() * 100,
    # FETCH DATA FROM SENSOR
    # humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    if humidity is not None and temperature is not None:
      # print(str(temperature))
      # print(str(humidity))
      # temperature = round(temperature, 2)
      # humidity = round(humidity, 2)

      tools = ToolChainSensor()

      print('temp ' + str(tools.insert_data(temperature)))
      # print('humi ' + str(tools.insert_data(humidity)))

      # print('ligh ' + str(tools.insert_data(light)))
      # print('mois ' + str(tools.insert_data(moisture)))

      # tools.set_hardware(temperature)
      # tools.set_hardware(humidity)

      # t_id = self.db.Sensor.find_one({'t': 'temperature'})['s_id']
      # h_id = self.db.Sensor.find_one({'t': 'humidity'})['s_id']

      # # INSERT IN DATABASE
      # tool_chain = Tools(self.db, plant_id)
      # tool_chain.notify_sensor([t_id, h_id], [temperature, humidity], mode)

      # # ACTIVATE MAILER
      # mailer = Mailer(self.db)
      # mailer.plant(plant_id, [t_id, h_id])

      # # INSERT DATA IN GENERAL STATUS LEDS
      # general_status(plant_id, [t_id, h_id], [temperature, humidity]).insert().set()

      # # IF == 1 insert also in legacy database else 100 records..
      # return tool_chain.change_detector([t_id, h_id], [temperature, humidity])

    # else:
    #   return -1

if __name__ == '__main__':
  # DHT22().get_data()
  import time
  # while True:
  DHT22().run()
  # print('done')
  # time.sleep(.5)
