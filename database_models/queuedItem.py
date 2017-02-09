import peewee
from peewee import *

from settings import *

class QueuedItem(peewee.Model):
    json = peewee.TextField()
    tweet_id = peewee.TextField()



    class Meta:
        database = MySQLDatabase(
            database_table,
            user=database_user,
            passwd=database_password
        )
        indexes = (
            (('tweet_id'), True),
        )


try:
    QueuedItem.create_table()
    print 'Queue created'
except:
    print 'Queue already created'
    pass
