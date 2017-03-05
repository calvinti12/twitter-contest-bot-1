from bot_meta import BotMeta
from settings.settings import *
import threading
import time
import datetime

from twitter import Twitter

twitter = Twitter(consumer_key, consumer_secret,
                  access_token_key, access_token_secret,
                  min_ratelimit, min_ratelimit_search, min_ratelimit_retweet)

meta = BotMeta()

def CheckRateLimit():
    c = threading.Timer(rate_limit_update_time, CheckRateLimit)
    c.daemon = True
    c.start()

    if twitter.rateHigh():
        print(
        "Ratelimit too low -> Cooldown (" + str(twitter.rate_limit[2]) + "%)")
        time.sleep(30)

    now = datetime.datetime.now()
    meta.save_meta_for_key('last_check_limit', now)

    twitter.updateRateLimitStatus()


# Update the Retweet queue (this prevents too many retweets happening at once.)
def UpdateQueue():
    u = threading.Timer(retweet_update_time, UpdateQueue)
    u.daemon = True
    u.start()

    now = datetime.datetime.now()
    meta.save_meta_for_key('last_update_queue', now)

    twitter.updateQueue()


def ScanForContests():
    t = threading.Timer(scan_update_time, ScanForContests)
    t.daemon = True
    t.start()

    now = datetime.datetime.now()
    meta.save_meta_for_key('last_scan', now)

    twitter.ScanForContests()



print "!!!!!!!!!!!!!!!!!!!!!!!!!! START TWEETBOT !!!!!!!!!!!!!!!!!!!!!!!!!!"
CheckRateLimit()
ScanForContests()
UpdateQueue()

while (True):
    time.sleep(1)
