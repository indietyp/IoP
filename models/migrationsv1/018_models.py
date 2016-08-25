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

    migrator.change_fields('sensorsatisfactionlevel', sensor=pw.BooleanField(default=False, null=True))
    migrator.remove_fields('sensorsatisfactionlevel', 'min_value', 'max_value', 'sensor')

    migrator.change_fields('sensorsetting', min_value=pw.FloatField(default=0, null=True),
        max_value=pw.FloatField(default=1, null=True))
    migrator.add_fields('sensorsetting', sensor=pw.BooleanField(default=False))

    migrator.drop_not_null('sensorsetting', 'min_value')

    migrator.drop_not_null('sensorsetting', 'max_value')


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.change_fields('sensorsetting', sensor=pw.ForeignKeyField(db_column='sensor_id', rel_model=Sensor, to_field='id'))

    migrator.add_not_null('sensorsetting', 'min_value')

    migrator.add_not_null('sensorsetting', 'max_value')

    migrator.add_fields(
        'sensorsatisfactionlevel',

        min_value=pw.FloatField(default=0, null=True),
        max_value=pw.FloatField(default=1, null=True),
        sensor=pw.BooleanField(default=False))
