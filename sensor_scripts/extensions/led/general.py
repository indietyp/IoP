import RPi.GPIO as GPIO
from models.plant import Plant
from tools.main import VariousTools
from models.sensor import Sensor, SensorStatus


class TrafficLight(object):
  """docstring for setStatus"""

  def __init__(self):
    pass

  @staticmethod
  def run():
    result = VariousTools.offline_check('generalleds', hardware=True, pins=[3, 6, 16])
    if result is True:
      setting = {'threat': 0, 'cautioning': 0, 'optimum': 0}
      plant = Plant.get(Plant.localhost == True)

      all_status = SensorStatus.select().where(SensorStatus.plant == plant)

      for status in all_status:
        setting[status.level.label] += 1

      GPIO.setmode(GPIO.BCM)
      # GREEN
      GPIO.setup(5, GPIO.OUT)
      GPIO.output(5, False)
      # YELLOW
      GPIO.setup(6, GPIO.OUT)
      GPIO.output(6, False)
      # RED
      GPIO.setup(13, GPIO.OUT)
      GPIO.output(13, False)

      if setting['threat'] > 0:
        GPIO.output(13, True)
      elif setting['cautioning'] > 0:
        GPIO.output(6, True)
      elif setting['optimum'] > 0:
        GPIO.output(5, True)
      # GPIO.cleanup()
if __name__ == "__main__":
  TrafficLight.run()
