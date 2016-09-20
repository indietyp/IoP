import RPi.GPIO as GPIO
from models.plant import Plant
from models.sensor import Sensor, SensorStatus


class TrafficLight(object):
  """docstring for setStatus"""
  def __init__(self):
    pass

  @staticmethod
  def run():
    setting = {'threat': 0, 'cautioning': 0, 'optimum': 0}
    plant = Plant.get(Plant.localhost == True)

    all_status = SensorStatus.select().where(SensorStatus.plant == plant)

    for status in all_status:
      setting[status.level.label] += 1


    GPIO.setup
    # GREEN
    GPIO.setup(03, GPIO.OUT)
    GPIO.output(03, False)
    # YELLOW
    GPIO.setup(06, GPIO.OUT)
    GPIO.output(06, False)
    # RED
    GPIO.setup(13, GPIO.OUT)
    GPIO.output(13, False)

    if setting['danger'] > 0:
      GPIO.output(13, True)
    elif setting['warning'] > 0:
      GPIO.output(06, True)
    elif setting['optima'] > 0:
      GPIO.output(03, True)

if __name__ == "__main__":
  TrafficLight.run()
