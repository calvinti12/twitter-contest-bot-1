import peewee
from peewee import *

from settings.settings import *

class SearchTerm(peewee.Model):
    term = peewee.TextField()

    class Meta:
        database = MySQLDatabase(
            database_table,
            user=database_user,
            passwd=database_password
        )
        indexes = (
            (('term'), True),
        )

try:
    SearchTerm.create_table()
    print 'Term created'
except:
    print 'Term already created'
    pass



class SearchTerms(object):

    def __init__(self):
        print "Search terms initiated"


    def count(self):
        return SearchTerm.select().count()

