from peewee import Model, CharField, AutoField, TextField, IntegerField, FloatField
from database_manager import DatabaseManager
import local_settings

database_manager = DatabaseManager(
    database_name=local_settings.DATABASE["name"],
    user=local_settings.DATABASE["user"],
    password=local_settings.DATABASE["password"],
    host=local_settings.DATABASE["host"],
    port=local_settings.DATABASE["port"],
)


class HomeAds(Model):
    id = AutoField()
    href = CharField()
    # city = CharField()
    price = CharField(null=True)
    # type = CharField()
    room = FloatField(null=True)
    space = CharField(null=True)
    address = TextField(null=True)
    title = TextField(null=True)
    description = TextField(null=True)
    image_urls = TextField(null=True)

    class Meta:
        database = database_manager.db


try:
    database_manager.create_tables(models=[HomeAds])
    print("Connect to DataBase Successfully!")
except Exception as error:
    print("Error", error)
finally:
    # closing database connection.
    if database_manager.db:
        database_manager.db.close()
