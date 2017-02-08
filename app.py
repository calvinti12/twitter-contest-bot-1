#!flask/bin/python
from flask import Flask, jsonify, render_template
from post_queue import PostQueue
from ignore_list import IgnoreList

app = Flask(__name__, static_url_path='')


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