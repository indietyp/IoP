from peewee import *
from settings.database import DATABASE_NAME

import datetime
db = SqliteDatabase(DATABASE_NAME)


class Person(Model):
  email     = CharField()
  name      = CharField()
  wizard    = BooleanField(default=False)

  class Meta:
    database = db


class Plant(Model):
  name        = CharField()
  location    = CharField()
  species     = CharField()
  interval    = IntegerField()

  person      = ForeignKeyField(Person)

  role        = CharField(default='master')
  ip          = CharField()
  localhost   = BooleanField(default=False)

  created_at  = DateTimeField(default=datetime.datetime.now)
  # Satisfactionstreak
  sat_streak  = IntegerField()

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
