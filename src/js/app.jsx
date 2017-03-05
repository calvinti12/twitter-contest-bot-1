import React, { Component } from 'react';
import ReactDOM from 'react-dom';

import Dashboard from './components/Dashboard';

// Let the window know there is a React element on the page
// This means the react dev tools will work
if (typeof window !== 'undefined') {
    window.React = React;
}

ReactDOM.render(
    <Dashboard />,
    document.getElementById('app')
);
