import peewee
from peewee import *

from settings.settings import *

class IgnoredItem(peewee.Model):
    tweet_id = peewee.CharField()

    class Meta:
        database = MySQLDatabase(
            database_table,
            user=database_user,
            passwd=database_password
        )

try:
    IgnoredItem.create_table()
    print 'Ignore list created'
except:
    print 'Ignore list already created'
    pass


class IgnoreList(object):

    def __init__(self):
        print 'init list of ignored items'

    def add(self, id):
        item = IgnoredItem(tweet_id=id)
        item.save()

    def list(self):
        ignore_list = list()
        for item in IgnoredItem.select():
            ignore_list.append(item.tweet_id)
        return ignore_list

    def list_as_json(self):
        ignore_list = list()
        for item in IgnoredItem.select():
            ignore_list.append({
                'id':item.id,
                'tweet_id': item.tweet_id})

        return ignore_list
