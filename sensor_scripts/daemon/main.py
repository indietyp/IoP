import sys
import time
from datetime import datetime, timedelta
from settings.debug import DEBUG

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

five_minutes = 5 * 60


def round_base(x, base=5):
  return int(base * round(float(x) / base))


def next_execution_seconds():
  # get current time
  current_time = datetime.now()

  # get time in 5 min future for execution
  future_datetime = current_time + timedelta(seconds=five_minutes)

  # round number so that it's every time 5,10.. and not going to be 6,11...
  minute = round_base(future_datetime.minute)

  # reconstruct executions time with new minutes
  future_datetime = datetime(future_datetime.year, future_datetime.month, future_datetime.day, future_datetime.hour, minute, 0)
  next_execution = future_datetime - current_time

  return next_execution.seconds


def main():
  try:
    while True:
      sleep_seconds = next_execution_seconds()
      print(sleep_seconds)

      time.sleep(sleep_seconds)
      # raise DebugInterrupt
  except KeyboardInterrupt:
    print('Bye!')
    sys.exit()
  except Exception as e:
    main() if DEBUG is False else print(e)


if __name__ == '__main__':
  main()
