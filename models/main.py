from peewee import SqliteDatabase, Model
from settings.database import DATABASE_NAME
from playhouse.shortcuts import RetryOperationalError


class RetrySqliteDatabase(RetryOperationalError, SqliteDatabase):
  pass


db = RetrySqliteDatabase(DATABASE_NAME)


class Base(Model):
  class Meta:
    database = db
