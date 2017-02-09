#!flask/bin/python
from flask import Flask, jsonify, render_template
from celery import Celery

broker_url = 'amqp://root:root@localhost:5672/app/'

from post_queue import PostQueue
from ignore_list import IgnoreList



app = Flask(__name__, static_url_path='')
app.config['CELERY_BROKER_URL'] = broker_url
app.config['CELERY_RESULT_BACKEND'] = broker_url

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


# @celery.task
# def startTweetBot(arg1, arg2):
#     # some long running task here
#     result = arg1 + arg2
#     print result
#     startTweetBot.apply_async(args=[10, result], countdown=5)
#
#
# startTweetBot.apply_async(args=[10, 20], countdown=5)
#


@app.route('/')
def root():

    return render_template('index.html')

@app.route('/tweetbot/api/v1.0/queue', methods=['GET'])
def get_queue():
    post_queue = PostQueue()
    backlog = post_queue.list_as_json()
    return jsonify({'backlog': backlog})


@app.route('/tweetbot/api/v1.0/ignored', methods=['GET'])
def get_ignored():
    ignore_queue = IgnoreList()
    ignored_list = ignore_queue.list_as_json()
    return jsonify({'ignored_list': ignored_list})






if __name__ == '__main__':
    app.run(debug=True)