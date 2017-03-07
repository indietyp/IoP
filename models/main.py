from peewee import SqliteDatabase, Model
from settings.database import DATABASE_NAME
from playhouse.shortcuts import RetryOperationalError


class RetrySqliteDatabase(RetryOperationalError, SqliteDatabase):
  pass


db = RetrySqliteDatabase(DATABASE_NAME, pragmas=(
    ('journal_mode', 'WAL'),
    ('synchronous', 'NORMAL')))

class Base(Model):
  class Meta:
    database = db
