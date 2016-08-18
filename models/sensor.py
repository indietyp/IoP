from peewee import *
import datetime
from settings.database import DATABASE_NAME
from models.plant import *

db = SqliteDatabase(DATABASE_NAME)


class Sensor(Model):
  model       = CharField()
  name        = CharField()
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


class SensorSatisfationLevel(Model):
  name        = CharField()

  class Meta:
    database  = db


class SensorStatus(Model):
  sensor      = ForeignKeyField(Sensor)
  plant       = ForeignKeyField(Plant)

  level       = ForeignKeyField(SensorSatisfationLevel)

  class Meta:
    database  = db


class SensorCount(Model):
  sensor      = ForeignKeyField(Sensor)
  plant       = ForeignKeyField(Plant)
  level       = ForeignKeyField(SensorSatisfationLevel)

  count       = IntegerField()

  class Meta:
    database  = db


class SensorSetting(Model):
  sensor      = ForeignKeyField(Sensor)
  plant       = ForeignKeyField(Plant)
  level       = ForeignKeyField(SensorSatisfationLevel)

  min_value   = FloatField()
  max_value   = FloatField()

  class Meta:
    database  = db


class SensorHardware(Model):
  label       = CharField()

  class Meta:
    database  = db


class SensorHardwareConnector(Model):
  sensor      = ForeignKeyField(Sensor)
  hardware    = ForeignKeyField(SensorHardware)

  class Meta:
    database = db

