import os
import json
import math
import time
from copy import deepcopy
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
    changelog = [0, 0, 0]
    if result:
      setting = {'threat': 0, 'cautioning': 0, 'optimum': 0}
      plant = Plant.get(localhost=True)

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

    basedir = os.path.dirname(os.path.realpath(__file__))
    neopixel = Adafruit_NeoPixel(1, 18)
    neopixel.begin()

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

    old = deepcopy(current)
    for i in range(0, steps + 1):
      color = []
      for pointer in range(len(bchange)):
        if bchange[pointer]:
          if not bcurrent[pointer]:
            x = i
            offset = current[pointer]
          else:
            x = steps - i
            offset = changelog[pointer]
          color.append(offset + int(abs(current[pointer] - changelog[pointer]) / steps * x))
        else:
          color.append(old[pointer])

      print(color)
      neopixel.setPixelColorRGB(0, color[0], color[1], color[2])
      neopixel.show()
      old = deepcopy(color)
      time.sleep(1 / 15)

    with open(basedir + '/ledstate.json', 'w') as out:
      out.write(json.dumps(color))

    time.sleep(1)
    neopixel.setPixelColorRGB(0, changelog[0], changelog[1], changelog[2])
    neopixel.show()

    return True

if __name__ == "__main__":
  TrafficLight.run()
