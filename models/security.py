from peewee import *

from settings.database import DATABASE_NAME

db = SqliteDatabase(DATABASE_NAME)


class KeyChain(Model):
  secret      = TextField()
  message     = TextField()

  application = CharField()

  class Meta:
    database  = db


class MailAccount(Model):
  account     = CharField()
  transport   = CharField(default='smtp')
  server      = CharField()
  encryption  = CharField(default='ssl')
  port        = IntegerField(default=465)

  daemon      = BooleanField(default=False)
  password    = ForeignKeyField(KeyChain)

  class Meta:
    database  = db
