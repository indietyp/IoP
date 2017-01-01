import uuid
import datetime
from peewee import *
from models.main import Base
from models.plant import Plant
# from settings.database import DATABASE_NAME
# db = SqliteDatabase(DATABASE_NAME)


class MeshMessage(Base):
  plant = ForeignKeyField(Plant)
  sender = ForeignKeyField(Plant, null=True, related_name='senders')
  received = BooleanField(default=True)

  uuid = UUIDField(unique=True, default=uuid.uuid4)
  priority = SmallIntegerField()

  code = IntegerField(null=True)
  a_message = CharField(null=True)
  b_message = CharField(null=True)
  c_message = CharField(null=True)
  d_message = CharField(null=True)

  created_at = DateTimeField(default=datetime.datetime.now)


class MeshObject(Base):
  ip = CharField()
  registered = BooleanField(default=True)

  created_at = DateTimeField(default=datetime.datetime.now)
