def exc():
  import os
  import json
  import math
  import time
  from copy import deepcopy
  from neopixel import Adafruit_NeoPixel
  basedir = os.path.dirname(os.path.realpath(__file__))

  steps = 60
  neopixel = Adafruit_NeoPixel(1, 18)
  neopixel.begin()

  setting = {'threat': 0, 'cautioning': 1, 'optimum': 0}
  changelog = [0, 0, 0]

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
  print(current)
  bcurrent = []
  bchange = []

  for pointer in range(len(current)):
    bcurrent.append(True if current[pointer] > changelog[pointer] else False)
    bchange.append(True if current[pointer] != changelog[pointer] else False)

  # pointers = []
  # for pointer in range(len(bchange)):
  #   if bchange[pointer]:
  #     pointers.append(pointer)

  # print(pointers)
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
        # color.append(offset + int(math.cos((1 / steps) * math.pi * x) * (abs(current[pointer] - changelog[pointer]) / 2) + (abs(current[pointer] - changelog[pointer]) / 2)))
      else:
        color.append(old[pointer])
    print(color)
    neopixel.setPixelColorRGB(0, color[0], color[1], color[2])
    neopixel.show()
    old = deepcopy(color)
    time.sleep(0.1)
    print(color)

  with open(basedir + '/ledstate.json', 'w') as out:
    out.write(json.dumps(old))

if __name__ == '__main__':
  exc()
