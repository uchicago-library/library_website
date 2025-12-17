const path = require('path')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')

module.exports = {
  context: __dirname,

  performance: {
    hints: false,
  },

  entry: {
    main: './base/static/base/js/index',
    NewsFeed: './lib_news/static/lib_news/js/NewsFeed',
    CGIMailForm: './base/static/base/js/CGIMailForm',
    CGIMailEditor: './cgimail_editor/static/cgimail_editor/js/CGIMailEditor',
  },

  output: {
    path: path.resolve('./base/static/bundles/'),
    filename: '[name]-bundle.js',
  },

  plugins: [
    new BundleTracker({ filename: './webpack-stats.json' }),
    new webpack.ProvidePlugin({
      process: 'process/browser',
    }),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: ['babel-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['*', '.js', '.jsx'],
    fallback: { util: require.resolve('util/'), stream: false },
  },
}
