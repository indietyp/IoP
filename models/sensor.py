from peewee import *
import datetime
from settings.database import DATABASE_NAME
from models.plant import *

db = SqliteDatabase(DATABASE_NAME)


class Sensor(Model):
  model       = CharField()
  name        = CharField(unique=True)
  unit        = CharField()

  min_value   = FloatField()
  max_value   = FloatField()

  persistant_offset = FloatField(default=1)
  persistant_hold   = IntegerField(default=2016)

  class Meta:
    database  = db


class SensorData(Model):
  value       = FloatField()
  plant       = ForeignKeyField(Plant)
  sensor      = ForeignKeyField(Sensor)

  persistant  = BooleanField(default=False)
  created_at  = DateTimeField(default=datetime.datetime.now)

  class Meta:
    database  = db


class SensorSatisfactionLevel(Model):
  label        = CharField()
  name_color   = CharField()
  hex_color    = CharField(null=True)

  class Meta:
    database  = db


class SensorStatus(Model):
  """current sensor satisfaction level"""
  sensor      = ForeignKeyField(Sensor)
  plant       = ForeignKeyField(Plant)

  level       = ForeignKeyField(SensorSatisfactionLevel)

  class Meta:
    database  = db


class SensorCount(Model):
  """count how long satisfaction level - for comparison"""
  sensor      = ForeignKeyField(Sensor)
  plant       = ForeignKeyField(Plant)
  level       = ForeignKeyField(SensorSatisfactionLevel)

  count       = IntegerField()

  class Meta:
    database  = db


class SensorSetting(Model):
  """Satisfactionlevel min and max value"""
  sensor      = ForeignKeyField(Sensor)
  plant       = ForeignKeyField(Plant)
  level       = ForeignKeyField(SensorSatisfactionLevel)

  min_value   = FloatField()
  max_value   = FloatField()

  class Meta:
    database  = db


class SensorDangerMessage(Model):
  plant       = ForeignKeyField(Plant)
  sensor      = ForeignKeyField(Sensor)
  level       = ForeignKeyField(SensorSatisfactionLevel)

  message     = TextField()
  value       = FloatField()

  sent        = BooleanField(default=False)
  created_at  = DateTimeField(default=datetime.datetime.now)

  class Meta:
    database  = db


class SensorHardware(Model):
  label           = CharField()
  function        = CharField(default='generic')
  last_execution  = DateTimeField(default=datetime.datetime.now, null=True)

  class Meta:
    database  = db


class SensorHardwareConnector(Model):
  sensor      = ForeignKeyField(Sensor)
  hardware    = ForeignKeyField(SensorHardware)

  class Meta:
    database = db

