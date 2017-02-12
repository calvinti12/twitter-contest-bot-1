import peewee
from peewee import *

from settings.settings import *

class BotMetaItem(peewee.Model):
    key = peewee.CharField()
    value = peewee.CharField()

    class Meta:
        database = MySQLDatabase(
            database_table,
            user=database_user,
            passwd=database_password
        )

try:
    BotMetaItem.create_table()
    print 'Meta DB created'
except:
    print 'Meta DB already created'
    pass



class BotMeta(object):

    def __init__(self):
        print 'init meta database'
        self.meta = BotMetaItem()


    def load_meta_for_key(self, key):
        try:
            meta = BotMetaItem.get(BotMetaItem.key==key)
            return meta.value
        except:
            return None

    def save_meta_for_key(self, key, value):
        try:
            # Update existing
            meta = BotMetaItem.get(BotMetaItem.key==key)
            # update value with new value
            meta.value = value
            meta.save()
        except:
            # Create new status entry
            meta = BotMetaItem(key=key, value=value)
            meta.save()