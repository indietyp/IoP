import math
import time
import RPi.GPIO as GPIO
from models.plant import Plant
from tools.main import VariousTools
from models.sensor import Sensor, SensorStatus


class TrafficLight(object):
  """docstring for setStatus"""

  def __init__(self):
    pass

  def newrun(steps=10):
    from neopixel import Adafruit_NeoPixel
    neopixel = Adafruit_NeoPixel(1, 18)
    neopixel.begin()

    # result = VariousTools.offline_check('generalleds', hardware=True, pins=[5, 6, 13])
    # if result is True:
    setting = {'threat': 0, 'cautioning': 0, 'optimum': 0}
    plant = Plant.get(localhost=True)
    changelog = [0, 0, 0]

    all_status = SensorStatus.select().where(SensorStatus.plant == plant)

    for status in all_status:
      setting[status.level.label] += 1

    # setting = {'threat': 1, 'cautioning': 2, 'optimum': 1}
    # changelog = [0, 0, 0]

    if setting['threat'] > 0:
      changelog[0] = 255
    elif setting['cautioning'] > 0:
      changelog[0] = 255
      changelog[1] = 255
    elif setting['optimum'] > 0:
      changelog[1] = 255

    current = neopixel.getPixelColor(0)
    bcurrent = []
    bchange = []

    for pointer in range(len(current)):
      bcurrent.append(True if current[pointer] >= changelog[pointer] else False)
      bchange.append(True if current[pointer] != changelog[pointer] else False)

    for i in range(0, steps + 1):
      color = []
      for pointer in range(len(bchange)):
        if bchange[pointer]:
          if not bcurrent[pointer]:
            x = steps - i
            # y = changelog[pointer]
            offset = current[pointer]
          else:
            x = i
            # y = current[pointer]
            offset = changelog[pointer]
          color.append(offset + int(math.cos((1 / steps) * math.pi * x) * (abs(current[pointer] - changelog[pointer]) / 2) + (abs(current[pointer] - changelog[pointer]) / 2)))
        else:
          color.append(current[pointer])
      neopixel.setPixelColorRGB(0, color[0], color[1], color[2])
      neopixel.show()
      time.sleep(.1)
      print(color)

  @staticmethod
  def run():
    result = VariousTools.offline_check('generalleds', hardware=True, pins=[5, 6, 13])
    if result is True:
      setting = {'threat': 0, 'cautioning': 0, 'optimum': 0}
      plant = Plant.get(localhost=True)

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
