import React, { Component } from 'react';

import TweetQueue from './TweetQueue';
import TwitterStatus from './TwitterStatus';
import SearchingStatus from './SearchingStatus';

class Dashboard extends Component {

    render() {

        return (
             <div className="dashboard">
                 <TwitterStatus />
                 <SearchingStatus />
                 <TweetQueue />
            </div>
        )

    }
}



export default Dashboard;