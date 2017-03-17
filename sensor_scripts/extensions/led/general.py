import os
import json
import math
import time
from models.plant import Plant
from tools.main import VariousTools
from neopixel import Adafruit_NeoPixel
from models.sensor import SensorStatus


class TrafficLight(object):
  """docstring for setStatus"""

  def __init__(self):
    pass

  @staticmethod
  def run(steps=120):
    result = VariousTools.offline_check('generalleds', hardware=False)
    if not result:
      return False

    basedir = os.path.dirname(os.path.realpath(__file__))
    neopixel = Adafruit_NeoPixel(1, 18)
    neopixel.begin()

    setting = {'threat': 0, 'cautioning': 0, 'optimum': 0}
    plant = Plant.get(localhost=True)
    changelog = [0, 0, 0]

    all_status = SensorStatus.select().where(SensorStatus.plant == plant)

    for status in all_status:
      setting[status.level.label] += 1

    if setting['threat'] > 0:
      changelog[0] = 255
    elif setting['cautioning'] > 0:
      changelog[0] = 255
      changelog[1] = 255
    elif setting['optimum'] > 0:
      changelog[1] = 255

    if os.path.isfile(basedir + '/ledstate.json'):
      with open(basedir + '/ledstate.json', 'r') as out:
        current = json.loads(out.read())
    else:
      raw = neopixel.getPixelColor(0)
      current = []

      for _ in range(3):
        calc = divmod(raw, 256)
        raw = calc[0]
        current.append(calc[1])

      current = current[::-1]

    if changelog == current:
      return True

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
            offset = current[pointer]
          else:
            x = i
            offset = changelog[pointer]
          color.append(offset + int(math.cos((1 / steps) * math.pi * x) * (abs(current[pointer] - changelog[pointer]) / 2) + (abs(current[pointer] - changelog[pointer]) / 2)))
        else:
          color.append(current[pointer])

      neopixel.setPixelColorRGB(0, color[0], color[1], color[2])
      neopixel.show()
      time.sleep(1 / 30)
      print(color)

    with open(basedir + '/ledstate.json', 'w') as out:
      out.write(json.dumps(color))

    return True

  # @staticmethod
  # def run():
  #   result = VariousTools.offline_check('generalleds', hardware=True, pins=[5, 6, 13])
  #   if result is True:
  #     setting = {'threat': 0, 'cautioning': 0, 'optimum': 0}
  #     plant = Plant.get(localhost=True)

  #     all_status = SensorStatus.select().where(SensorStatus.plant == plant)

  #     for status in all_status:
  #       setting[status.level.label] += 1

  #     GPIO.setmode(GPIO.BCM)
  #     # GREEN
  #     GPIO.setup(5, GPIO.OUT)
  #     GPIO.output(5, False)
  #     # YELLOW
  #     GPIO.setup(6, GPIO.OUT)
  #     GPIO.output(6, False)
  #     # RED
  #     GPIO.setup(13, GPIO.OUT)
  #     GPIO.output(13, False)

  #     if setting['threat'] > 0:
  #       GPIO.output(13, True)
  #     elif setting['cautioning'] > 0:
  #       GPIO.output(6, True)
  #     elif setting['optimum'] > 0:
  #       GPIO.output(5, True)
  #     # GPIO.cleanup()
if __name__ == "__main__":
  TrafficLight.run()
