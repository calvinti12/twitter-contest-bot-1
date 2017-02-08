from TwitterAPI import TwitterAPI
from log import *

class Twitter(object):

    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret, min_ratelimit, min_ratelimit_search, min_ratelimit_retweet):
        print 'Twitter'
        self.api = TwitterAPI(consumer_key, consumer_secret,
                         access_token_key, access_token_secret)
        self.rate_limit = [999, 999, 100]
        self.rate_limit_search = [999, 999, 100]
        self.min_ratelimit = min_ratelimit
        self.min_ratelimit_search = min_ratelimit_search
        self.min_ratelimit_retweet = min_ratelimit_retweet

    def updateRateLimitStatus(self):
        r = self.api.request('application/rate_limit_status').json()

        for res_family in r['resources']:
            for res in r['resources'][res_family]:
                limit = r['resources'][res_family][res]['limit']
                remaining = r['resources'][res_family][res]['remaining']
                percent = float(remaining) / float(limit) * 100

                if res == "/search/tweets":
                    self.rate_limit_search = [limit, remaining, percent]

                if res == "/application/rate_limit_status":
                    self.rate_limit = [limit, remaining, percent]

                # print(res_family + " -> " + res + ": " + str(percent))
                if percent < 5.0:
                    LogAndPrint(res_family + " -> " + res + ": " + str(
                        percent) + "  !!! <5% Emergency exit !!!")
                    sys.exit(res_family + " -> " + res + ": " + str(
                        percent) + "  !!! <5% Emergency exit !!!")
                elif percent < 30.0:
                    LogAndPrint(res_family + " -> " + res + ": " + str(
                        percent) + "  !!! <30% alert !!!")
                elif percent < 70.0:
                    print(res_family + " -> " + res + ": " + str(percent))

    # def followUser(self, username):
    #     try:
    #         r = twitter.api.request('friendships/create', {'screen_name': username })
    #         CheckError(r)
    #         LogAndPrint("Follow: " + username)

    def rateHigh(self):
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

