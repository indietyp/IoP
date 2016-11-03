from peewee import *
from settings.database import DATABASE_NAME
import uuid

import datetime
db = SqliteDatabase(DATABASE_NAME)


class MessagePreset(Model):
  name = CharField(unique=True)
  uuid = UUIDField(default=uuid.uuid4)

  message = TextField()
  created_at = DateTimeField(default=datetime.datetime.now)
  default = BooleanField(default=False)

  class Meta:
    database = db


class Person(Model):
  email     = CharField()
  name      = CharField()

  uuid      = UUIDField(default=uuid.uuid4, unique=True)
  wizard    = BooleanField(default=False)
  preset    = ForeignKeyField(MessagePreset, null=True)

  class Meta:
    database = db


class Plant(Model):
  name        = CharField()
  location    = CharField()
  species     = CharField()
  interval    = IntegerField()
  uuid        = UUIDField(default=uuid.uuid4, unique=True)

  person      = ForeignKeyField(Person)

  role        = CharField(default='master')
  ip          = CharField()
  localhost   = BooleanField(default=False)

  created_at  = DateTimeField(default=datetime.datetime.now)
  # Satisfactionstreak
  sat_streak  = IntegerField()
  persistant_hold   = IntegerField(default=2016)

  class Meta:
    database  = db


class PlantNetworkStatus(Model):
  name        = CharField()

  class Meta:
    database  = db


class PlantNetworkUptime(Model):
  plant       = ForeignKeyField(Plant)
  status      = ForeignKeyField(PlantNetworkStatus)

  overall     = FloatField()
  current     = FloatField()

  class Meta:
    database  = db
