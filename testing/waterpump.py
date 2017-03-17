import RPi.GPIO as GPIO
import time

def test():
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
  try:
    while dc <= 100 and not limited:
      dc += 5
      print(dc)
      if dc > 100 and not limited:
        dc = 100
      # else:
      p.ChangeDutyCycle(dc)
      # counter += 1
        # if counter % 2 == 0:
          # print(counter)
          # limited = self.check(samples=3)
      time.sleep(.1)
  except:
    pass
  for dc in range(dc, -1, -5):
    print(dc)
    p.ChangeDutyCycle(dc)
    time.sleep(0.1)
  p.stop()
  GPIO.output(27, False)
  GPIO.output(22, False)
