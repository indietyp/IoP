import os
import sys
import time
import atexit
from datetime import datetime, timedelta

from models.plant import Plant
from settings.debug import DEBUG

# from sensor_scripts.core.dht import DHT22
# from sensor_scripts.core.tsl2561 import TSL2561
# from sensor_scripts.core.moisture import GenericMoisture

# from tools.debug import DebugInterrupt
# loop
#   --> current time
#   --> current time + 5
#   --> wait until
#   --> --> execute 4 scripts (if 30 min use *args for trigger persitant)
#   --> --> --> get data
#   --> --> --> execute helper
#   --> --> --> --> insert into database (mySQL - peewee)
#   --> --> --> --> --> insert into 5 min
#   --> --> --> --> --> check if 30 min or change of (in database - persistant_offset_trigger)
#   --> --> --> --> --> if persistant == True (passed var - don't check)
#   --> --> --> --> --> return if so
#   --> --> --> --> send signal to mesh
#   --> --> --> --> do hardware stuff (hardware id gets transmitted - saved in database)
#   --> --> --> return status insertation
#   --> --> --> status 1: triggered
#   --> --> --> --> reset value to 0
#   --> --> --> status 0: not triggered
#   --> --> --> --> add value to + 5
pid_file = './daemon.pid'

class SensorDaemon(object):

  def __init__(self):
    pass

  def round_base(self, x, base=5):
    return int(base * round(float(x) / base))

  def next_execution_seconds(self):
    # get current time
    current_time = datetime.now()

    # get time in 5 min future for execution
    five_minutes = 5 * 60
    future_datetime = current_time + timedelta(seconds=five_minutes)

    # round number so that it's every time 5,10.. and not going to be 6,11...
    print(str(future_datetime))
    minute = self.round_base(future_datetime.minute)
    if minute == 60:
      minute = 59

    # reconstruct execution time with new minutes
    future_datetime = datetime(future_datetime.year,
                               future_datetime.month,
                               future_datetime.day,
                               future_datetime.hour,
                               minute,
                               0)
    print(str(future_datetime))

    next_execution = future_datetime - current_time
    print(next_execution)

    return next_execution.seconds

  def run(self):
    if not os.path.isfile(pid_file) and self.verify() is True:
      with open(pid_file, 'w') as output:
        output.write(str(os.getpid()))

      try:
        while True:
          sleep_seconds = self.next_execution_seconds()
          time.sleep(sleep_seconds)
          print('Hellou!')

          # DHT22.run()
          # GenericMoisture.run()
          # TSL2561.run()
      except KeyboardInterrupt:
        print('Bye!')
        sys.exit()
      except Exception as e:
        self.run() if DEBUG is False else print(e)
      finally:
        self.exit()
    else:
      print('process already running')

  def exit(self):
    if os.path.isfile(pid_file):
      os.remove(pid_file)

  def verify(self):
    try:
      Plant.get(Plant.localhost == True)
      return True
    except:
      return False

if __name__ == '__main__':
  SensorDaemon().run()
