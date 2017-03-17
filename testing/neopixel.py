def exc():
  import math
  import time
  from neopixel import Adafruit_NeoPixel

  steps = 25
  neopixel = Adafruit_NeoPixel(1, 18)
  neopixel.begin()

  setting = {'threat': 0, 'cautioning': 0, 'optimum': 2}
  changelog = [0, 0, 0]

  if setting['threat'] > 0:
    changelog[0] = 255
  elif setting['cautioning'] > 0:
    changelog[0] = 255
    changelog[1] = 255
  elif setting['optimum'] > 0:
    changelog[1] = 255

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

if __name__ == '__main__':
  exc()