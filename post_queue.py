import json
import peewee
from peewee import *

db = MySQLDatabase('twitter-comp', user='root',passwd='root')

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


class PostQueue(object):

    def __init__(self):
        print "Tweet queue initiated"

    def add(self, item):
        json_data = json.dumps(item)
        tweet_id=item['id']
        item = QueuedItem(json=json_data, tweet_id=tweet_id)
        item.save()

    def count(self):
        return QueuedItem.select().count()

    def first(self):
        data =  QueuedItem.select().get()
        return json.loads(data.json)

    def popFirst(self):
        #first = self.first().id
        #QueuedItem.delete().where(QueuedItem.id == first).execute()
        QueuedItem.execute_sql('DELETE from queueditem LIMIT 1')
