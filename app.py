#!flask/bin/python
from settings.settings import *
from flask import Flask, jsonify, render_template, send_from_directory, request, Response

import ast

from slackbot import get_channel_id_from_name, send_message

from twitter import Twitter
from bot_meta import BotMeta

# Setup Flask App
app = Flask(__name__, static_url_path='')


# Create Twitter object
twitter = Twitter(consumer_key, consumer_secret,
                 access_token_key, access_token_secret,
                 min_ratelimit, min_ratelimit_search, min_ratelimit_retweet)

# Create the meta object that loads/saves details to the DB
meta = BotMeta()


# Setup the routes for Flask
@app.route('/')
def root():
    return render_template('index.html')


@app.route('/tweetbot/api/v1.0/status', methods=['GET'])
def get_status():
    status = twitter.getState()
    # print status['rate']
    rate =  ast.literal_eval( status['rate'] )
    rate_limit = rate[0]
    available = rate[1]
    percent_remaining = rate[2]

    state = {}
    state['rate_limit'] = rate_limit
    state['available'] = available
    state['percent_remaining'] = percent_remaining
    state['status'] = status['state']

    return jsonify(state)

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


@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)



@app.route('/slack', methods=['POST'])
def inbound_slack():
    print request.form.get('token')
    if request.form.get('token') == SLACK_WEBHOOK_SECRET:
        channel = request.form.get('channel_name')
        # username = request.form.get('user_name')
        # text = request.form.get('text')
        # inbound_message = username + " in " + channel + " says: " + text
        # print(inbound_message)

        channel_id = get_channel_id_from_name(channel)

        queue_length = twitter.queue_length()

        status = twitter.getState()
        rate = ast.literal_eval(status['rate'])
        percent_remaining = rate[2]

        message = "Queue: %s with rate limit @ %s" % (queue_length, percent_remaining)

        if channel_id is not False:
            send_message(channel_id, message)

    return Response(), 200



if __name__ == '__main__':
    app.run(debug=True)