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

    migrator.add_fields(
        'plant',

        persistant_hold=pw.IntegerField(default=2016))

    # migrator.add_not_null('meshmessage', 'created_at')

    migrator.remove_fields('sensor', 'persistant_hold')


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.add_fields(
        'sensor',

        persistant_hold=pw.IntegerField(default=2016))

    # migrator.drop_not_null('meshmessage', 'created_at')

    migrator.remove_fields('plant', 'persistant_hold')

    migrator.add_fields(
        'person',

        preset=pw.ForeignKeyField(db_column='preset_id', null=True, rel_model=migrator.orm['messagepreset'], to_field='id'))
