#!flask/bin/python
from settings import *
from datetime import timedelta
from flask import Flask, jsonify, render_template
from celery import Celery
from celery.task import periodic_task

from twitter import Twitter
# from post_queue import PostQueue
from ignore_list import IgnoreList
from log import *

# Setup Flask App
app = Flask(__name__, static_url_path='')
app.config['CELERY_BROKER_URL'] = celery_broker_url
app.config['CELERY_RESULT_BACKEND'] = celery_broker_url

# Setup Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Create queues, and twitter object
twitter = Twitter(consumer_key, consumer_secret,
                 access_token_key, access_token_secret,
                 min_ratelimit, min_ratelimit_search, min_ratelimit_retweet)
ignore = IgnoreList()
# queue = PostQueue()

#Schedule tasks with beat
@periodic_task(run_every=timedelta(seconds=rate_limit_update_time))
def CheckRateLimit():
    twitter.updateRateLimitStatus()


@periodic_task(run_every=timedelta(seconds=retweet_update_time))
def UpdateQueue():
    twitter.updateQueue()


@periodic_task(run_every=timedelta(seconds=scan_update_time))
# Scan for new contests, but not too often because of the rate limit.
def ScanForContests():

    # Check if thw twitter object (rate limit) allows this roundof searches
    if twitter.canSearch():

        # Loop through the search queries
        for search_query in search_queries:

            try:
                query_results = twitter.search(search_query)
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

                    ignore_list_local = ignore.list()
                    contains_blocked_keywords = twitter.CheckForBlockedKeywords(
                        item)

                    if not original_id in ignore_list_local and not contains_blocked_keywords:

                        if not original_screen_name in ignore_list_local:

                            if not screen_name in ignore_list_local:

                                if item[
                                    'retweet_count'] > retweet_threshold:

                                    twitter.queue_add(item)

                                    if is_retweet:
                                        print(
                                        id + " - " + screen_name + " retweeting " + original_id + " - " + original_screen_name + ": " + text)
                                        ignore.add(original_id)

                                    else:
                                        print(
                                        id + " - " + screen_name + ": " + text)
                                        ignore.add(id)

                        else:
                            if contains_blocked_keywords:
                                ignore.add(id)
                                print "blocked keywords - not adding"

            except Exception as e:
                print(
                "Could not connect to TwitterAPI - are your credentials correct?")
                print("Exception: " + str(e))





@app.route('/')
def root():
    return render_template('index.html')


@app.route('/tweetbot/api/v1.0/status', methods=['GET'])
def get_status():
    status = twitter.getState()
    return jsonify(status)


@app.route('/tweetbot/api/v1.0/queue', methods=['GET'])
def get_queue():
    backlog = twitter.queue_list_as_json()
    return jsonify({'backlog': backlog})


@app.route('/tweetbot/api/v1.0/ignored', methods=['GET'])
def get_ignored():
    ignore_queue = IgnoreList()
    ignored_list = ignore_queue.list_as_json()
    return jsonify({'ignored_list': ignored_list})


if __name__ == '__main__':
    app.run(debug=True)