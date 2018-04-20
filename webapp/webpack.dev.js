const path = require('path') 
const merge = require('webpack-merge');
const common = require('./webpack.common.js');


module.exports = merge(common, {
  output: {
    filename: '[name].bundle.js',
  },
  devServer: {
    contentBase: [ path.resolve(__dirname, 'assets') ],
    progress: true,
    host: '0.0.0.0',
    port: 80,
    historyApiFallback: true,
    watchOptions: {
      poll: 500
    },
  },
});
