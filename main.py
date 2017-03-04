from settings.settings import *
import threading
import time

from twitter import Twitter

twitter = Twitter(consumer_key, consumer_secret,
                  access_token_key, access_token_secret,
                  min_ratelimit, min_ratelimit_search, min_ratelimit_retweet)


def CheckRateLimit():
    c = threading.Timer(rate_limit_update_time, CheckRateLimit)
    c.daemon = True
    c.start()

    if twitter.rateHigh():
        print(
        "Ratelimit too low -> Cooldown (" + str(twitter.rate_limit[2]) + "%)")
        time.sleep(30)

    twitter.updateRateLimitStatus()


# Update the Retweet queue (this prevents too many retweets happening at once.)
def UpdateQueue():
    u = threading.Timer(retweet_update_time, UpdateQueue)
    u.daemon = True
    u.start()
    twitter.updateQueue()


def ScanForContests():
    t = threading.Timer(scan_update_time, ScanForContests)
    t.daemon = True
    t.start()

    twitter.ScanForContests();



print "!!!!!!!!!!!!!!!!!!!!!!!!!! START TWEETBOT !!!!!!!!!!!!!!!!!!!!!!!!!!"
CheckRateLimit()
ScanForContests()
UpdateQueue()

while (True):
    time.sleep(1)
