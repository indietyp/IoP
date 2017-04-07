def measure():
  from machine import Pin, I2C
  from time import sleep
  import ntptime
  import time
  import ubinascii
  import ustruct
  import json

  ntptime.settime()

  with open('config.json', 'r') as out:
    config = json.loads(out.read())

  if 'sleep' in config:
    start = int(config['sleep']['min']) / 100
    stop = int(config['sleep']['max']) / 100
    led = True if start <= time.localtime()[3] <= stop else False
  else:
    led = True

  if 'range' in config:
    rng = config['range']
  else:
    rng = {'min': 60, 'max': 80}

  i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
  address = 0x20

  median = []

  alert = Pin(12, Pin.OUT)
  green = Pin(13, Pin.OUT)
  red = Pin(15, Pin.OUT)

  if led:
    alert.value(1)

  for i in range(6):
    result = i2c.readfrom_mem(address, 0, 2)
    result = ustruct.pack('>1h', *ustruct.unpack('<1h', result))
    median.append(int(ubinascii.hexlify(result).decode(), 16) / 65535 * 100)  # 2 bytes - max value == 65535
    sleep(0.5)

  alert.value(0)
  median = sum(median) / len(median)
  if median >= rng['min'] and median <= rng['max']:
    if led:
      green.value(1)
    else:
      green.value(0)

    red.value(0)
  else:
    green.value(0)

    if led:
      red.value(1)
    else:
      red.value(0)

  print(median)
  return median
