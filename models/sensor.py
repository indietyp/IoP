import uuid
import datetime
from peewee import *
from models.plant import *
from models.main import Base
# from settings.database import DATABASE_NAME
# db = SqliteDatabase(DATABASE_NAME)


class Sensor(Base):
  model       = CharField()
  name        = CharField(unique=True)
  unit        = CharField()
  uuid        = UUIDField(default=uuid.uuid4)

  min_value   = FloatField()
  max_value   = FloatField()

  persistant_offset = FloatField(default=1)
  # persistant_hold   = IntegerField(default=2016)


class SensorData(Base):
  value       = FloatField()
  plant       = ForeignKeyField(Plant, index=True)
  sensor      = ForeignKeyField(Sensor, index=True)

  persistant  = BooleanField(default=False)
  created_at  = DateTimeField(default=datetime.datetime.now)


class SensorSatisfactionLevel(Base):
  label        = CharField()
  name_color   = CharField()
  hex_color    = CharField(null=True)


class SensorStatus(Base):
  """current sensor satisfaction level - high <-> low"""
  sensor      = ForeignKeyField(Sensor)
  plant       = ForeignKeyField(Plant)
  level       = ForeignKeyField(SensorSatisfactionLevel)

  status      = BooleanField(default=False)  # low = False, high = True


class SensorCount(Base):
  """count how long satisfaction level - for comparison"""
  sensor      = ForeignKeyField(Sensor)
  plant       = ForeignKeyField(Plant)
  level       = ForeignKeyField(SensorSatisfactionLevel)

  count       = IntegerField()


class SensorSatisfactionValue(Base):
  """Satisfactionlevel min and max value"""
  sensor       = ForeignKeyField(Sensor)
  plant        = ForeignKeyField(Plant)
  level        = ForeignKeyField(SensorSatisfactionLevel)
  uuid         = UUIDField(default=uuid.uuid4)

  inherited    = BooleanField(default=False)

  min_value    = FloatField(default=0, null=True)
  max_value    = FloatField(default=1, null=True)


class SensorDangerMessage(Base):
  plant       = ForeignKeyField(Plant)
  sensor      = ForeignKeyField(Sensor)
  level       = ForeignKeyField(SensorSatisfactionLevel)

  message     = TextField()
  value       = FloatField()

  sent        = BooleanField(default=False)
  sent_time   = DateTimeField(null=True)

  created_at  = DateTimeField(default=datetime.datetime.now)


class SensorHardware(Base):
  label           = CharField()
  function        = CharField(default='generic')
  last_execution  = DateTimeField(default=datetime.datetime.now, null=True)


class SensorHardwareConnector(Base):
  sensor      = ForeignKeyField(Sensor)
  hardware    = ForeignKeyField(SensorHardware)


class SensorDataPrediction(Base):
  plant       = ForeignKeyField(Plant, index=True)
  sensor      = ForeignKeyField(Sensor, index=True)

  value       = FloatField()
  time        = DateTimeField()

  created_at  = DateTimeField(default=datetime.datetime.now)
