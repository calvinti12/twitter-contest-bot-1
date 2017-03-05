import React, { Component } from 'react';

import $ from 'jquery';

import LoadingIndicator from './LoadingIndicator';

class TweetQueue extends Component {

    constructor(props) {
        super(props);

        this.state = {
            tweets:[],
            loading: false
        };

        this.getTweets = this.getTweets.bind(this);

        setInterval(this.getTweets, (5 * 1000));
    }

    getTweets() {
        if (this.state.loading === false) {

            this.setState(
                function(prevState, props){
                    return {
                        loading: true
                    }
                }
            );

            let queue_end_point = '/tweetbot/api/v1.0/queue';

            $.ajax({
                type: 'GET',
                url: queue_end_point,
                success: function (data) {

                    this.setState(
                        function (prevState, props) {
                            return {
                                loading: false,
                                tweets: data.backlog
                            }
                        })
                }.bind(this)
            });
        }

    }

    render() {

        let tweets = this.state.tweets.map(function(tweet) {

            return (
                <li key={tweet.id}>
                    {tweet.json.text}
                </li>
            )

        });

        return (
            <div>
                <h2>Tweet queue ( {this.state.tweets.length} )</h2>
                <ul>
                    {tweets}
                </ul>
                <LoadingIndicator loading={this.state.loading} />
            </div>
        )
    }

}


export default TweetQueue;