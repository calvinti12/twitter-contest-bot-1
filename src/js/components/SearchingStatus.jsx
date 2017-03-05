import React, { Component } from 'react';

import $ from 'jquery';

import LoadingIndicator from './LoadingIndicator';

class SearchingStatus extends Component {


    constructor(props) {
        super(props);

        this.state = {
            current_search_term: '',
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

            let queue_end_point = '/tweetbot/api/v1.0/search-status';

            $.ajax({
                type: 'GET',
                url: queue_end_point,
                success: function (data) {

                    this.setState(
                        function (prevState, props) {
                            return {
                                loading: false,
                                current_search_term: data.searching_status,
                            }
                        })
                }.bind(this)
            });
        }
    }

    render() {

        return (
            <div>
                <h2>Current search</h2>
                <h3>{this.state.current_search_term}</h3>
                <LoadingIndicator loading={this.state.loading} />
            </div>
        )
    }
}


export default SearchingStatus;