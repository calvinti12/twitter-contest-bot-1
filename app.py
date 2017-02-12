#!flask/bin/python
from settings.settings import *
from datetime import timedelta
from flask import Flask, jsonify, render_template
from celery import Celery
from celery.task import periodic_task

from twitter import Twitter
from bot_meta import BotMeta

# Setup Flask App
app = Flask(__name__, static_url_path='')
app.config['CELERY_BROKER_URL'] = celery_broker_url
app.config['CELERY_RESULT_BACKEND'] = celery_broker_url

# Setup Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Create Twitter object
twitter = Twitter(consumer_key, consumer_secret,
                 access_token_key, access_token_secret,
                 min_ratelimit, min_ratelimit_search, min_ratelimit_retweet)

# Create the meta object that loads/saves details to the DB
meta = BotMeta()

# Schedule tasks with beat
@periodic_task(run_every=timedelta(seconds=rate_limit_update_time))
def CheckRateLimit():
    twitter.updateRateLimitStatus()


@periodic_task(run_every=timedelta(seconds=retweet_update_time))
def UpdateQueue():
    twitter.updateQueue()


@periodic_task(run_every=timedelta(seconds=scan_update_time))
def scanForContests():
    twitter.ScanForContests()


# Setup the routes for Flask
@app.route('/')
def root():
    return render_template('index.html')


@app.route('/tweetbot/api/v1.0/status', methods=['GET'])
def get_status():
    status = twitter.getState()
    return jsonify(status)

@app.route('/tweetbot/api/v1.0/search-status', methods=['GET'])
def get_search_status():
    searching_status = meta.load_meta_for_key('searching')
    return jsonify({ 'searching_status' : searching_status })


@app.route('/tweetbot/api/v1.0/queue', methods=['GET'])
def get_queue():
    backlog = twitter.queue_list_as_json()
    return jsonify({'backlog': backlog})


@app.route('/tweetbot/api/v1.0/ignored', methods=['GET'])
def get_ignored():
    ignore_queue = IgnoreList()
    ignored_list = ignore_queue.list_as_json()
    return jsonify({'ignored_list': ignored_list})


@app.route('/tweetbot/api/v1.0/manage/initialise', methods=['GET'])
def upload_ignored():
    if not meta.load_meta_for_key('initialised'):
        twitter.importIgnoreList()
        meta.save_meta_for_key('initialised', True)
        print 'Ignore list imported from disk'
    else:
        print 'Already Imported Ignore list - To import again set the database key "initialised" to False!!'
    return jsonify({'loaded': 'loaded'})


if __name__ == '__main__':
    app.run(debug=True)