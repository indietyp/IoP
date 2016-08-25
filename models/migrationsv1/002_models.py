"""Peewee migrations: ::

    > Model = migrator.orm['name']

    > migrator.sql(sql)
    > migrator.python(func, *args, **kwargs)
    > migrator.create_model(Model)
    > migrator.remove_model(Model, cascade=True)
    > migrator.add_fields(Model, **fields)
    > migrator.change_fields(Model, **fields)
    > migrator.remove_fields(Model, *field_names, cascade=True)
    > migrator.rename_field(Model, old_field_name, new_field_name)
    > migrator.rename_table(Model, new_table_name)
    > migrator.add_index(Model, *col_names, unique=False)
    > migrator.drop_index(Model, *col_names)
    > migrator.add_not_null(Model, *field_names)
    > migrator.drop_not_null(Model, *field_names)
    > migrator.add_default(Model, field_name, default)

"""

import datetime as dt
import peewee as pw


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    @migrator.create_model
    class SensorHardware(pw.Model):
        label = pw.CharField(max_length=255)

    @migrator.create_model
    class SensorHardwareConnector(pw.Model):
        sensor = pw.ForeignKeyField(db_column='sensor_id', rel_model=migrator.orm['sensor'], to_field='id')
        hardware = pw.ForeignKeyField(db_column='hardware_id', rel_model=SensorHardware, to_field='id')



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('sensorhardwareconnector')

    migrator.remove_model('sensorhardware')
