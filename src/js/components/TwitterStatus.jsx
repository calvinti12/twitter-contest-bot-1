import React, { Component } from 'react';


import $ from 'jquery';

import LoadingIndicator from './LoadingIndicator';


class TwitterStatus extends Component {


    constructor(props) {
        super(props);

        this.state = {
            rate_limit: 0,
            available: 0,
            percent_remaining: 0,
            loading: false
        };

        this.getStatus = this.getStatus.bind(this);

        setInterval(this.getStatus, (2 * 1000));
    }


    getStatus() {
        if (this.state.loading === false) {

            this.setState(
                function(prevState, props){
                    return {
                        loading: true
                    }
                }
            );

            let queue_end_point = '/tweetbot/api/v1.0/status';

            $.ajax({
                type: 'GET',
                url: queue_end_point,
                success: function (data) {

                    this.setState(
                        function (prevState, props) {
                            return {
                                loading: false,
                                rate_limit: data.rate_limit,
                                available: data.available,
                                percent_remaining: data.percent_remaining,
                                status: data.status
                            }
                        })
                }.bind(this)
            });
        }
    }

    render() {

        return (
                <div>
                    <h2>API Status</h2>
                     <ul>
                        <li>Status: { this.state.status }</li>
                        <li>Limit: { this.state.available }/{ this.state.rate_limit } ({ Math.round(this.state.percent_remaining)}%)</li>
                     </ul>
                    <LoadingIndicator loading={this.state.loading} />
                </div>
            )

    }
}

export default TwitterStatus;