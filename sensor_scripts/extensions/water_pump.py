import sys
import time
import logging
import tools.logger
import RPi.GPIO as GPIO
from models.plant import Plant
from tools.main import VariousTools
from tools.sensor import ToolChainSensor
from sensor_scripts.driver.mcp3002 import mcp3002
from models.sensor import Sensor, SensorStatus, SensorSatisfactionValue, SensorSatisfactionLevel, SensorData
logger = logging.getLogger('sensor_scripts')


class WaterPump:
  def __init__(self):
    self.sensor = Sensor.get(name='moisture')
    self.plant = Plant.get(localhost=True)

    data = {'plant': self.plant,
            'sensor': self.sensor}
    self.collection = ToolChainSensor().get_sensor_satification_value(data)

  def check(self, samples=10):
    values = []
    for i in range(0, samples):
      values.append(mcp3002().read_pct(0, 1))
    average = sum(values) / float(len(values))

    current = {'minimum': - sys.maxsize,
               'satisfaction': None}
    optimum = None

    for satisfaction in self.collection:
      if satisfaction['inherited']:
        satisfaction['min_value'] = self.sensor.min_value
        satisfaction['max_value'] = self.sensor.max_value

      if satisfaction['level']['color'] == 'green':
        optimum = satisfaction

      if current['minimum'] < satisfaction['min_value']:
        if satisfaction['min_value'] <= average <= satisfaction['max_value']:
          current['satisfaction'] = satisfaction
          current['minimum'] = satisfaction['min_value']

    if optimum is None:
      return True

    if current['satisfaction']['level']['color'] != 'green' and average <= optimum['max_value']:
      return False
    else:
      return True

  def run(self):
    result = VariousTools.offline_check('waterpump', hardware=False)
    if result:
      status = SensorStatus.get(SensorStatus.sensor == self.sensor,
                                SensorStatus.plant == self.plant)

      optimum = SensorSatisfactionLevel.get(SensorSatisfactionValue.label == 'optimum')

      satisfaction = SensorSatisfactionValue.get(SensorSatisfactionValue.sensor == self.sensor,
                                                 SensorSatisfactionValue.plant == self.plant,
                                                 SensorSatisfactionValue.level == optimum)

      latest = SensorData.select(SensorData.sensor == self.sensor,
                                 SensorData.plant == self.plant).order_by(SensorData.created_at.desc()).limit(1)[0]

      if status.level.label == 'threat' and latest.value < satisfaction.min_value:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.setup(27, GPIO.OUT)
        GPIO.setup(22, GPIO.OUT)

        GPIO.output(27, True)
        GPIO.output(22, False)

        p = GPIO.PWM(17, 500)
        p.start(0)

        counter = 0
        dc = 0

        limited = False
        while dc <= 100 and not limited:
          dc += 5
          print(dc)
          if dc > 100 and not limited:
            dc = 100
          else:
            p.ChangeDutyCycle(dc)

          counter += 1
          if counter % 2 == 0:
            limited = self.check(samples=3)
          time.sleep(.1)

        for dc in range(dc, -1, -5):
          p.ChangeDutyCycle(dc)
          time.sleep(0.1)

        p.stop()
        GPIO.output(27, False)
        GPIO.output(22, False)


if __name__ == "__main__":
  pass
  # tester = WaterPump()
  # tester.set()
