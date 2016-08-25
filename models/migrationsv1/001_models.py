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
    class KeyChain(pw.Model):
        secret = pw.TextField()
        message = pw.TextField()
        application = pw.CharField(max_length=255)

    @migrator.create_model
    class Person(pw.Model):
        email = pw.CharField(max_length=255)
        name = pw.CharField(max_length=255)
        wizard = pw.BooleanField(default=False)

    @migrator.create_model
    class Plant(pw.Model):
        name = pw.CharField(max_length=255)
        location = pw.CharField(max_length=255)
        species = pw.CharField(max_length=255)
        interval = pw.IntegerField()
        person = pw.ForeignKeyField(db_column='person_id', rel_model=Person, to_field='id')
        role = pw.CharField(default='master', max_length=255)
        ip = pw.CharField(max_length=255)
        localhost = pw.BooleanField(default=False)
        created_at = pw.DateTimeField()
        sat_streak = pw.IntegerField()

    @migrator.create_model
    class PlantNetworkStatus(pw.Model):
        name = pw.CharField(max_length=255)

    @migrator.create_model
    class PlantNetworkUptime(pw.Model):
        plant = pw.ForeignKeyField(db_column='plant_id', rel_model=Plant, to_field='id')
        status = pw.ForeignKeyField(db_column='status_id', rel_model=PlantNetworkStatus, to_field='id')
        overall = pw.FloatField()
        current = pw.FloatField()

    @migrator.create_model
    class Sensor(pw.Model):
        model = pw.CharField(max_length=255)
        name = pw.CharField(max_length=255)
        unit = pw.CharField(max_length=255)
        min_value = pw.FloatField()
        max_value = pw.FloatField()
        persistant_offset = pw.FloatField(default=1)

    @migrator.create_model
    class SensorData(pw.Model):
        value = pw.FloatField()
        plant = pw.ForeignKeyField(db_column='plant_id', rel_model=Plant, to_field='id')
        sensor = pw.ForeignKeyField(db_column='sensor_id', rel_model=Sensor, to_field='id')
        persistant = pw.BooleanField(default=True)
        created_at = pw.DateTimeField()

    @migrator.create_model
    class SensorSatisfationLevel(pw.Model):
        name = pw.CharField(max_length=255)

    @migrator.create_model
    class SensorCount(pw.Model):
        sensor = pw.ForeignKeyField(db_column='sensor_id', rel_model=Sensor, to_field='id')
        plant = pw.ForeignKeyField(db_column='plant_id', rel_model=Plant, to_field='id')
        level = pw.ForeignKeyField(db_column='level_id', rel_model=SensorSatisfationLevel, to_field='id')
        count = pw.IntegerField()

    @migrator.create_model
    class SensorSetting(pw.Model):
        sensor = pw.ForeignKeyField(db_column='sensor_id', rel_model=Sensor, to_field='id')
        plant = pw.ForeignKeyField(db_column='plant_id', rel_model=Plant, to_field='id')
        level = pw.ForeignKeyField(db_column='level_id', rel_model=SensorSatisfationLevel, to_field='id')
        min_value = pw.FloatField()
        max_value = pw.FloatField()

    @migrator.create_model
    class SensorStatus(pw.Model):
        sensor = pw.ForeignKeyField(db_column='sensor_id', rel_model=Sensor, to_field='id')
        plant = pw.ForeignKeyField(db_column='plant_id', rel_model=Plant, to_field='id')
        level = pw.ForeignKeyField(db_column='level_id', rel_model=SensorSatisfationLevel, to_field='id')



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('sensorstatus')

    migrator.remove_model('sensorsetting')

    migrator.remove_model('sensorcount')

    migrator.remove_model('sensorsatisfationlevel')

    migrator.remove_model('sensordata')

    migrator.remove_model('sensor')

    migrator.remove_model('plantnetworkuptime')

    migrator.remove_model('plantnetworkstatus')

    migrator.remove_model('plant')

    migrator.remove_model('person')

    migrator.remove_model('keychain')
