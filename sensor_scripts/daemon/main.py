import os
import sys
import time
import atexit
import logging
import tools.logger
from datetime import datetime, timedelta

from models.plant import Plant
from models.sensor import Sensor
from settings.debug import DEBUG, DUMMYPLANT
from settings.database import DATABASE_NAME
from tools.main import VariousTools
from multiprocessing import Process

logger = logging.getLogger('sensor_scripts')

if not DUMMYPLANT:
  from sensor_scripts.core.dht import DHT22
  from sensor_scripts.core.tsl2561 import TSL2561
  from sensor_scripts.core.moisture import GenericMoisture
else:
  from tools.simulate import PlantSimulate

real_path = os.path.realpath(__file__)
pid_file = os.path.dirname(real_path) + '/daemon.pid'


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

    logger.info('next planned execution: {}'.format(future_datetime))
    next_execution = future_datetime - current_time
    logger.debug('exact time till next execution: {}'.format(next_execution))

    return next_execution.seconds

  def execute(self):
    DHT22.run()
    GenericMoisture.run()
    TSL2561.run()

  def simulate(self):
    target = Plant.get(Plant.localhost == True)
    source = Plant.get(Plant.name == 'marta')
    for sensor in Sensor.select():
      logger.info(sensor.name)
      logger.debug(PlantSimulate().run(target, sensor, source))

  def run(self):
    if not os.path.isfile(pid_file) and VariousTools.verify_database():
      with open(pid_file, 'w') as output:
        output.write(str(os.getpid()))

      try:
        while True:
          sleep_seconds = self.next_execution_seconds()
          time.sleep(sleep_seconds)
          if not DUMMYPLANT:
            exc = Process(target=self.execute)
            exc.daemon = True
            exc.start()
            logger.debug('mode: real')
            logger.info('finished')
          else:
            exc = Process(target=self.simulate)
            exc.daemon = True
            exc.start()
            logger.debug('mode: simulated')
            logger.info('finished')

      except KeyboardInterrupt:
        print('Bye!')
        sys.exit()
      except Exception as e:
        if DEBUG is False:
          self.run()
        else:
          print(e)
      finally:
        self.exit()
    else:
      if not VariousTools.verify_database():
        logger.error('aborted action - database required - no database provided')

      if os.path.isfile(pid_file):
        logger.error('process already running')

  def exit(self):
    if os.path.isfile(pid_file):
      os.remove(pid_file)

  def verify(self):
    try:
      Plant.get(Plant.localhost == True)
      return True
    except Exception as e:
      logger.warning(e)
      return False


# only for security! That the file is removed on termination
atexit.register(SensorDaemon().exit)

if __name__ == '__main__':
  print('start')
  if len(sys.argv) < 2:
    logger.info('running standard configuration')
    SensorDaemon().run()
  elif sys.argv[1] == 'force' or True:
    logger.info('forcing start - deleting ' + pid_file + ' if found')
    SensorDaemon().exit()
    SensorDaemon().run()
