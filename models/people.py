from peewee import *
from settings.database import DATABASE_NAME

db = SqliteDatabase(DATABASE_NAME)


class Person(Model):
  email     = CharField()
  name      = CharField()
  wizard    = BooleanField(default=False)

  class Meta:
    database = db
