import os

from TwitterAPI import TwitterAPI
from log import *

from settings.settings import *

from post_queue import PostQueue
from ignore_list import IgnoreList
from bot_meta import BotMeta

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
        self.queue = PostQueue()
        self.ignore = IgnoreList()
        self.meta = BotMeta()


    def importIgnoreList(self):
        ignore_list = list()
        if os.path.isfile('ignorelist'):
            with open('ignorelist') as f:
                ignore_list = f.read().splitlines()
            f.close()
        for item in ignore_list:
            # Try to save to the database
            # print item
            self.ignore.add(item)


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

        self.meta.save_meta_for_key('current_rate', rateArray)
        self.meta.save_meta_for_key('current_state', status_text)

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
        self.rate_limit = self.meta.load_meta_for_key('current_rate')

        if self.rate_limit[2] < self.min_ratelimit:
            return True
        return False

    def canSearch(self):
        if not self.meta.load_meta_for_key('current_rate')[2] < self.min_ratelimit_search:
            return True
        return False

    def canRetweet(self):
        if not self.meta.load_meta_for_key('current_rate')[2] < self.min_ratelimit_retweet:
            return True
        return False

    def getState(self):
        state = self.meta.load_meta_for_key('current_state')
        rate = self.meta.load_meta_for_key('current_rate')

        return { 'state': state, 'rate': rate }

    def updateQueue(self):
        if self.queue.count() > 0:

            if self.canRetweet():
                post = self.queue.first()

                self.CheckForFollowRequest(post)
                self.CheckForFavoriteRequest(post)

                r = self.api.request('statuses/retweet/:' + str(post['id']))
                CheckError(r)

                # Remove from Queue
                self.queue.popFirst()
                # Add to ignore list
                self.ignore.add(post['id'])

    def CheckForFollowRequest(self, item):
        text = item['text']
        if any(x in text.lower() for x in follow_keywords):
            try:
                self.followUser(
                    item['retweeted_status']['user']['screen_name'])

            except:
                self.followUser(item['user']['screen_name'])

    def CheckForFavoriteRequest(self, item):
        text = item['text']

        if any(x in text.lower() for x in fav_keywords):
            try:
                r = self.api.request('favorites/create',
                                        {'id': item['retweeted_status']['id']})
                CheckError(r)
                LogAndPrint("Favorite: " + str(item['retweeted_status']['id']))
            except:
                r = self.api.request('favorites/create', {'id': item['id']})
                CheckError(r)
                LogAndPrint("Favorite: " + str(item['id']))

    def CheckForBlockedKeywords(self, item):
        text = item['text']

        if any(x in text.lower() for x in blocked_keywords):
            # Blocked
            return True
        # Not blocked
        return False

    def queue_list_as_json(self):
        return self.queue.list_as_json()

    def queue_add(self, item):
        self.queue.add(item)

    # Scan for new contests, but not too often because of the rate limit.
    def ScanForContests(self):

        # Check if thw twitter object (rate limit) allows this roundof searches
        if self.canSearch():


            # Loop through the search queries
            for search_query in search_queries:
                LogAndPrint("Searching for : " + str(search_query))
                self.meta.save_meta_for_key('searching', search_query)
                try:
                    query_results = self.search(search_query)
                    c = 0

                    for item in query_results:



                        c = c + 1
                        user_item = item['user']
                        screen_name = user_item['screen_name']
                        text = item['text']
                        text = text.replace("\n", "")
                        id = str(item['id'])
                        original_id = id
                        original_screen_name = screen_name
                        is_retweet = 0

                        if 'retweeted_status' in item:
                            is_retweet = 1
                            original_item = item['retweeted_status']
                            original_id = str(original_item['id'])
                            original_user_item = original_item['user']
                            original_screen_name = original_user_item[
                                'screen_name']

                        ignore_list_local = self.ignore.list()
                        contains_blocked_keywords = self.CheckForBlockedKeywords(
                            item)

                        if contains_blocked_keywords:
                            LogAndPrint( "Keywords are blocked, skip this entry: " + str(text) )
                            if is_retweet:
                                self.ignore.add(original_id)
                            else:
                                self.ignore.add(id)
                        else:
                            if not original_id in ignore_list_local and not contains_blocked_keywords:

                                if not original_screen_name in ignore_list_local:

                                    if not screen_name in ignore_list_local:

                                        if item['retweet_count'] > retweet_threshold:

                                            self.queue_add(item)

                                            if is_retweet:
                                                print(
                                                    id + " - " + screen_name + " retweeting " + original_id + " - " + original_screen_name + ": " + text)
                                                self.ignore.add(original_id)

                                            else:
                                                print(
                                                    id + " - " + screen_name + ": " + text)
                                                self.ignore.add(id)

                                else:
                                    if contains_blocked_keywords:
                                        self.ignore.add(id)
                                        print "blocked keywords - not adding"

                except Exception as e:
                    print(
                        "Could not connect to TwitterAPI - are your credentials correct?")
                    print("Exception: " + str(e))

            self.meta.save_meta_for_key('searching', False)