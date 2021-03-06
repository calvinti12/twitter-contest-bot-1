import json
from database_models.queuedItem import *

class PostQueue(object):

    def __init__(self):
        print "Tweet queue initiated"

    def add(self, item):
        json_data = json.dumps(item)
        tweet_id = item['id']
        item = QueuedItem(json=json_data, tweet_id=tweet_id)
        item.save()

    def count(self):
        return QueuedItem.select().count()

    def first(self):
        data = QueuedItem.select().get()
        return json.loads(data.json)

    def popFirst(self):
        first = QueuedItem.select().get()
        print ("Deleting: " + str(first.tweet_id))
        first.delete_instance()

    def list_as_json(self):
        queue_list = list()
        for item in QueuedItem.select():
            queue_list.append({
                'id':item.id,
                'json': json.loads(item.json),
                'tweet_id': item.tweet_id})

        return queue_list