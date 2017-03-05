import React, { Component } from 'react';



class LoadingIndicator extends Component {

    render() {

        if (this.props.loading === true) {
            return (
                <div>
                    Loading...
                </div>
            )
        } else {
            return (
                <div>
                    ...
                </div>
            )
        }
    }
}


export default LoadingIndicator;