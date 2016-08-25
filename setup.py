import socket

from models.plant import Plant
from models.plant import Person
from models.security import MailAccount
from models.security import KeyChain as keychain
from tools.security import KeyChain
from models.sensor import Sensor
from models.sensor import SensorHardware, SensorHardwareConnector
from models.sensor import *

print('Welcome to the configuration of IoP')
if Plant.select().count() == 0:
  print('CREATE FIRST PLANT: \n\n')
  plant = Plant()
  plant.name = input('How do you want to call your first plant? ').lower()
  plant.location = input('The location? ').lower()
  plant.species = input('The species? ').lower()

  def interval():
    int_interval = input('emailing interval? (int) (h) ')

    if int_interval.isdigit() is True:
      return int(int_interval)
    else:
      return interval()

  plant.interval = interval()

  person = Person()
  print('\nto:')
  person.name = input('     Name: ')
  person.email = input('    Email: ')
  person.wizard = True
  person.save()
  print('\n')

  plant.person = person

  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("gmail.com", 80))

  plant.ip = s.getsockname()[0]
  plant.localhost = True

  s.close()

  plant.sat_streak = 0
  plant.save()
  input('Plant setup finished! Continue? (if not ^C)\n')

if MailAccount.select().where(MailAccount.daemon == True).count() == 0:
  daemon_account = MailAccount()
  print('email account is using smtp and ssl at port 465')
  daemon_account.account = input('EMail account: ')
  daemon_account.server = input('EMail server: ')
  daemon_account.daemon = True

  password = keychain()
  encrypted = KeyChain().encrypt(input('Password: '))
  password.secret = encrypted[0]
  password.message = encrypted[1]
  password.application = 'mailer'
  password.save()

  daemon_account.password = password
  daemon_account.save()


def model(sensor):
  model_str = input('model: ')

  if sensor == 'temperature' or sensor == 'humidity':
    if model_str != 'DHT22' and model_str != 'DHT11':
      print('temperature valid values - DHT11 and DHT22, pls try again\n')
      model(sensor)

  return model_str

for sensor in ['temperature', 'light', 'humidity', 'moisture']:
  if Sensor.select().where(Sensor.name == sensor).count() == 0:
    print('\n\nCREATE {}: \n\n'.format(sensor.upper()))
    db_sensor = Sensor()
    db_sensor.name = sensor
    db_sensor.model = model(sensor)
    db_sensor.unit = input('unit (only for display) ')
    db_sensor.min_value = input('minimum value? ')
    db_sensor.max_value = input('maximum value? ')
    db_sensor.persistant_offset = input('to persistant offset? ')

    db_sensor.save()

all_sensors = ['temperature', 'light', 'humidity', 'moisture']
if SensorHardware.select().count() == 0:
  print('doing some other stuff')
  hardware_collection = {'led_traffic_light': all_sensors,
                         'led_bar': ['moisture'],
                         'display': ['temperature', 'humidity'],
                         'mailer': all_sensors,
                         'water_pump': ['moisture']}

  for hardware, values in hardware_collection.items():
    current = SensorHardware(label=hardware, function='execute_' + hardware)
    current.save()

    for sensor in values:
      sensor = Sensor.get(name=sensor)
      c = SensorHardwareConnector(hardware=current, sensor=sensor)
      c.save()


def isfloat(text):
  try:
    return float(input(text))
  except:
    print('try again')
    return isfloat(text)


for level in ['threat', 'cautioning', 'optimum']:
  if SensorSatisfactionLevel.select()\
                            .where(SensorSatisfactionLevel.label == level)\
                            .count() == 0:
    satisfaction_level = SensorSatisfactionLevel()
    satisfaction_level.label = level
    print(level)
    satisfaction_level.name_color = input('color: ')
    satisfaction_level.save()

    for single_sensor in all_sensors:
      print('Sensor: ' + single_sensor)
      obj_sensor = Sensor.get(Sensor.name == single_sensor)
      plant = Plant.get(Plant.localhost == True)

      print('Sensor min - ' + str(obj_sensor.min_value))
      print('Sensor max - ' + str(obj_sensor.max_value))

      sensor_satisfaction_value = SensorSatisfactionValue()

      sensor_satisfaction_value.plant = plant
      sensor_satisfaction_value.sensor = obj_sensor.id
      sensor_satisfaction_value.level = satisfaction_level
      # print(sensor_satisfaction_value.sensor)

      if level == 'threat':
        sensor_satisfaction_value.inherited = True
        sensor_satisfaction_value.min_value = None
        sensor_satisfaction_value.max_value = None
      else:
        sensor_satisfaction_value.min_value = isfloat('min_value: ')
        sensor_satisfaction_value.max_value = isfloat('max_value: ')

      # print(sensor_satisfaction_value.sensor)
      sensor_satisfaction_value.save()
