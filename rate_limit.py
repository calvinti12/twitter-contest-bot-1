import peewee
from peewee import *

from settings import *


class RateLimit(peewee.Model):
    current_rate = peewee.CharField()
    current_state = peewee.CharField()

    class Meta:
        database = MySQLDatabase(
            database_table,
            user=database_user,
            passwd=database_password
        )

        try:
            RateLimit.create_table()
            print 'Ignore list created'
        except:
            print 'Ignore list already created'
            pass