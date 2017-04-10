from peewee import *
from models.main import Base
from settings.database import DATABASE_NAME
import uuid

import datetime
db = SqliteDatabase(DATABASE_NAME)


class MessagePreset(Base):
  name        = CharField(unique=True)
  uuid        = UUIDField(default=uuid.uuid4, unique=True)

  message     = TextField()
  created_at  = DateTimeField(default=datetime.datetime.now)
  default     = BooleanField(default=False)


class Person(Base):
  email     = CharField()
  name      = CharField()

  uuid      = UUIDField(default=uuid.uuid4, unique=True)
  wizard    = BooleanField(default=False)
  preset    = ForeignKeyField(MessagePreset, null=True)


class Plant(Base):
  name        = CharField()
  location    = CharField()
  species     = CharField()
  interval    = IntegerField(default=6)  # hours (messaging interval)
  uuid        = UUIDField(default=uuid.uuid4, unique=True)

  person      = ForeignKeyField(Person)
  role        = CharField(default='master')
  ip          = CharField()
  localhost   = BooleanField(default=False)
  active      = BooleanField(default=True)
  host        = BooleanField(default=False)

  sat_streak      = IntegerField()  # satisfactionstreak
  persistant_hold = IntegerField(default=2016)  # times (5 minute interval)
  connection_lost = IntegerField(default=5)  # minutes (notification to wizard after plant lost)

  created_at  = DateTimeField(default=datetime.datetime.now)


class PlantNetworkStatus(Base):
  name        = CharField()


class PlantNetworkUptime(Base):
  plant       = ForeignKeyField(Plant)
  status      = ForeignKeyField(PlantNetworkStatus)

  overall     = FloatField()
  current     = FloatField()
