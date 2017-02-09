from settings import *
import threading
import time


from twitter import Twitter
from post_queue import PostQueue
from ignore_list import IgnoreList

from log import LogAndPrint, CheckError



twitter = Twitter(consumer_key, consumer_secret,
                 access_token_key, access_token_secret,
                 min_ratelimit, min_ratelimit_search, min_ratelimit_retweet)

ignore = IgnoreList()
queue = PostQueue()


def CheckRateLimit():
    c = threading.Timer(rate_limit_update_time, CheckRateLimit)
    c.daemon = True
    c.start()

    if twitter.rateHigh():
        print("Ratelimit too low -> Cooldown (" + str(twitter.rate_limit[2]) + "%)")
        time.sleep(30)

    twitter.updateRateLimitStatus()


# Update the Retweet queue (this prevents too many retweets happening at once.)
def UpdateQueue():
    u = threading.Timer(retweet_update_time, UpdateQueue)
    u.daemon = True
    u.start()

    print("=== CHECKING RETWEET QUEUE ===")

    print("Queue length: " + str(queue.count()))

    if queue.count() > 0:

        if twitter.canRetweet():

            post = queue.first()
            print("first post: " + str(post['id']))

            LogAndPrint(
                "Retweeting: " + str(post['id']) + " " + str(
                    post['text'].encode('utf8')))

            CheckForFollowRequest(post)
            CheckForFavoriteRequest(post)

            r = twitter.api.request('statuses/retweet/:' + str(post['id']))
            CheckError(r)

            queue.popFirst()

        else:

            print("Ratelimit at " + str(
                twitter.rate_limit[2]) + "% -> pausing retweets")



# Check if a post requires you to follow the user.
# Be careful with this function! Twitter may write ban your
# application for following too aggressively
def CheckForFollowRequest(item):
    text = item['text']
    if any(x in text.lower() for x in follow_keywords):
        try:
            twitter.followUser(item['retweeted_status']['user']['screen_name'])
            # r = twitter.api.request('friendships/create', {'screen_name': item['retweeted_status']['user']['screen_name']})
            # CheckError(r)
            # LogAndPrint("Follow: " + item['retweeted_status']['user']['screen_name'])
        except:
            twitter.followUser(item['user']['screen_name'])
            # user = item['user']
            # screen_name = user['screen_name']
            # r = twitter.api.request('friendships/create', {'screen_name': screen_name})
            # CheckError(r)
            # LogAndPrint("Follow: " + screen_name)


# Check if a post requires you to favorite the tweet.
# Be careful with this function! Twitter may write ban your
# application for favoriting too aggressively
def CheckForFavoriteRequest(item):
    text = item['text']

    if any(x in text.lower() for x in fav_keywords):
        try:
            r = twitter.api.request('favorites/create', {'id': item['retweeted_status']['id']})
            CheckError(r)
            LogAndPrint("Favorite: " + str(item['retweeted_status']['id']))
        except:
            r = twitter.api.request('favorites/create', {'id': item['id']})
            CheckError(r)
            LogAndPrint("Favorite: " + str(item['id']))


def CheckForBlockedKeywords(item):
    text = item['text']

    if any(x in text.lower() for x in blocked_keywords):
        print("Blocked for keyword: " + str(text))
        # Blocked
        return True
    # Not blocked
    return False



# Scan for new contests, but not too often because of the rate limit.
def ScanForContests():
    t = threading.Timer(scan_update_time, ScanForContests)
    t.daemon = True
    t.start()

    if twitter.canSearch():

        print("=== SCANNING FOR NEW CONTESTS ===")

        for search_query in search_queries:

            print("Getting new results for: " + search_query)

            try:
                r = twitter.api.request(
                    'search/tweets', {'q': search_query,
                                      'result_type': "mixed", 'count': 100})
                CheckError(r)
                c=0

                for item in r:

                    c=c+1
                    user_item = item['user']
                    screen_name = user_item['screen_name']
                    text = item['text']
                    text = text.replace("\n", "")
                    id = str(item['id'])
                    original_id=id
                    original_screen_name = screen_name
                    is_retweet = 0

                    if 'retweeted_status' in item:

                        is_retweet = 1
                        original_item = item['retweeted_status']
                        original_id = str(original_item['id'])
                        original_user_item = original_item['user']
                        original_screen_name = original_user_item['screen_name']

                    ignore_list_local = ignore.list()
                    contains_blocked_keywords = CheckForBlockedKeywords(item)

                    if not original_id in ignore_list_local and not contains_blocked_keywords:

                        if not original_screen_name in ignore_list_local:

                            if not screen_name in ignore_list_local:

                                if item['retweet_count'] > retweet_threshold:

                                    queue.add(item)

                                    if is_retweet:
                                        print(id + " - " + screen_name + " retweeting " + original_id + " - " + original_screen_name + ": " + text)
                                        ignore.add(original_id)

                                    else:
                                        print(id + " - " + screen_name + ": " + text)
                                        ignore.add(id)

                        else:
                            if contains_blocked_keywords:
                                ignore.add(id)
                                print "blocked keywords - not adding"

                        # else:
                        #
                        #
                        # 	if is_retweet:
                        # 		print(id + " ignored: " + original_screen_name + " on ignore list")
                        # 	else:
                        # 		print(original_screen_name + " in ignore list")

                    # else:
                    #
                    # 	if is_retweet:
                    # 		print(id + " ignored: " + original_id + " on ignore list")
                    # 	else:
                    # 		print(id + " in ignore list")

                # print("Got " + str(c) + " results")

            except Exception as e:
                print("Could not connect to TwitterAPI - are your credentials correct?")
                print("Exception: " + str(e))

    else:

        print("Search skipped! Queue: " + str(queue.count()) + " Ratelimit: " + str(twitter.rate_limit_search[1]) + "/" + str(ratelimit_search[0]) + " (" + str(ratelimit_search[2]) + "%)")


CheckRateLimit()
ScanForContests()
UpdateQueue()

while (True):
    time.sleep(1)
