# get current time - done
#   first time round up by 5 - done
# pause until - done
# execute 'dummy' scripts
# get time + 5 - done
# delete seconds + miliseconds, timerounder - done

# 2 Databases
#   detailed
#   -> 100 records per sensor per plant
#   normal
# 5 min executer
# if change < 1
#   -> execute 30min
#     -> reset counter of happend
#   -> if no such change after counter == 6
#     -> reset counter


import pause
import datetime


def round_up(x, base=5):
  return x + base if x % base == 0 else x + base - x % base


def round_base(x, base=5):
  return int(base * round(float(x) / base))


def time_overflow_correction(minute, hour):
  return (minute, hour) if minute < 59 else (minute - 59, hour + 1)

current_time = datetime.datetime.now()

minute, hour = time_overflow_correction(current_time.minute, current_time.hour)
minute = round_up(minute)

next_execution = datetime.datetime(current_time.year, current_time.month, current_time.day, hour, minute, 0)

print(next_execution)
while True:

  pause.until(next_execution)

  current_time = datetime.datetime.now()
  minute, hour = time_overflow_correction(current_time.minute + 5, current_time.hour)
  minute = round_base(minute)
  next_execution = datetime.datetime(current_time.year, current_time.month, current_time.day, hour, minute, 0)

  print(next_execution)
