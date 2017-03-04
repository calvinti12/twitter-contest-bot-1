var webpack = require('webpack');
var path = require('path');

module.exports = {
  // entry: path.resolve(__dirname, './src/js/app.jsx'),
  output: {
    //path: path.resolve(__dirname, './dist'),
    filename: 'comments.js'
  },
  externals: {
      // require("jquery") is external and available
      //  on the global var jQuery
      "jquery": "$"
  },

  module: {
    loaders: [
      {
        test: /\.json$/,
        loader: "json-loader"
      },
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: "babel-loader"
      }
    ]
  }
};