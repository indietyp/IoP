from peewee import *

from settings.database import DATABASE_NAME

db = SqliteDatabase(DATABASE_NAME)


class KeyChain(Model):
  secret      = TextField()
  message     = TextField()

  application = CharField()

  class Meta:
    database  = db
