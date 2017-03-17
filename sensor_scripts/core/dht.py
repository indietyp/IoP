import tools.logger
import Adafruit_DHT

from models.plant import Plant
from models.sensor import Sensor
from tools.sensor import ToolChainSensor


class DHT22:
  """readout for DHT22/11 sensor"""

  def __init__(self):
    pass

  @staticmethod
  def run():
    plant = Plant.get(localhost=True)

    # PARSE PARAMETERS
    temperature = {'sensor': Sensor.select().where(Sensor.name == 'temperature')[0],
                   'plant': plant}
    humidity = {'sensor': Sensor.select().where(Sensor.name == 'humidity')[0],
                'plant': plant}

    if temperature['sensor'].model == humidity['sensor'].model:
      sensor = Adafruit_DHT.DHT22 if temperature['sensor'].model == 'DHT22' else Adafruit_DHT.DHT11
    pin = 26

    # FETCH DATA FROM SENSOR
    humidity['value'], temperature['value'] = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
      toolchain = ToolChainSensor()

      if toolchain.insert_data(temperature):
        toolchain.set_hardware(temperature)

      if toolchain.insert_data(humidity):
        toolchain.set_hardware(humidity)

if __name__ == '__main__':
  DHT22.run()
