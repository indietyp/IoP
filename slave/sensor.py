def measure():
  from machine import Pin, I2C
  from time import sleep
  import ubinascii
  import ustruct

  i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
  address = 0x20

  median = []
  alert = Pin(12, Pin.OUT)
  alert.value(1)

  for i in range(5):
    result = i2c.readfrom_mem(address, 0, 2)
    result = ustruct.pack('>1h', *ustruct.unpack('<1h', result))
    median.append(int(ubinascii.hexlify(result).decode(), 16) / 65535 * 100)  # 2 bytes - max value == 65535
    sleep(0.5)

  alert.value(0)
  return sum(median) / len(median)
