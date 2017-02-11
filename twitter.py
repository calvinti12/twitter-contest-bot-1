from TwitterAPI import TwitterAPI
from log import *
import peewee
from peewee import *

from settings import *


class TwitterStatus(peewee.Model):
    current_rate = peewee.CharField()
    current_state = peewee.CharField()

    class Meta:
        database = MySQLDatabase(
            database_table,
            user=database_user,
            passwd=database_password
        )

try:
    TwitterStatus.create_table()
    print 'Twitter Status DB Table created'
except:
    print 'Twitter Status DB Table exists'
    pass

class Twitter(object):

    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret, min_ratelimit, min_ratelimit_search, min_ratelimit_retweet):
        print 'Twitter initiated'
        self.api = TwitterAPI(consumer_key, consumer_secret,
                         access_token_key, access_token_secret)
        self.rate_limit = [999, 999, 100]
        self.rate_limit_search = [999, 999, 100]
        self.min_ratelimit = min_ratelimit
        self.min_ratelimit_search = min_ratelimit_search
        self.min_ratelimit_retweet = min_ratelimit_retweet

    def search(self, query):
        results = self.api.request(
            'search/tweets', {
                'q': query,
                'result_type': "mixed",
                'count': 100
            }
        )
        CheckError(results)
        return results

    def updateState(self, rateArray):
        self.rate_limit = rateArray
        percent = rateArray[2]
        status_text = 'OK'
        if percent < 5.0:
            status_text = "CRITICAL"
        elif percent < 30.0:
            status_text = "WARNING"
        elif percent < 50.0:
            status_text = "NOTICE"

        try:
            # Update existing
            state = TwitterStatus.select().get()
            state.current_rate = rateArray
            state.current_state = status_text
            state.save()
        except:
            # Create new status entry
            item = TwitterStatus(current_rate=rateArray, current_state='initial')
            item.save()

    def updateRateLimitStatus(self):
        r = self.api.request('application/rate_limit_status').json()

        for res_family in r['resources']:
            for res in r['resources'][res_family]:
                limit = r['resources'][res_family][res]['limit']
                remaining = r['resources'][res_family][res]['remaining']
                percent = float(remaining) / float(limit) * 100

                if res == "/search/tweets":
                    self.updateState([limit, remaining, percent])

                if res == "/application/rate_limit_status":
                    self.updateState([limit, remaining, percent])

    def followUser(self, username):
        # try:
        r = self.api.request('friendships/create', {'screen_name': username })
        if 'errors' in r.json():
            raise ValueError('error: ' + str(r['errors'][0]['message']))
        else:
            LogAndPrint("Followed: " + username)

    def rateHigh(self):
        #get rate from DB
        self.rate_limit = TwitterStatus.select().get()

        if self.rate_limit[2] < self.min_ratelimit:
            return True
        return False

    def canSearch(self):
        if not self.rate_limit_search[2] < self.min_ratelimit_search:
            return True
        return False

    def canRetweet(self):
        if not self.rate_limit[2] < self.min_ratelimit_retweet:
            return True
        return False

    def getState(self):
        state = TwitterStatus.select().get()
        return { 'state': state.current_state, 'rate': state.current_rate }
