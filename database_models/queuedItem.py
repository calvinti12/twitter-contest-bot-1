import peewee
from peewee import *

db = MySQLDatabase('twitter-comp', user='root', passwd='root')


class QueuedItem(peewee.Model):
    json = peewee.TextField()
    tweet_id = peewee.TextField()



    class Meta:
        database = db
        indexes = (
            (('tweet_id'), True),
        )


try:
    QueuedItem.create_table()
    print 'Queue created'
except:
    print 'Queue already created'
    pass
