const path = require('path');

const outputDirectory = '../static/disambiguator_ui/js'


module.exports = {
  entry: './src/index.js',
  output: {
    path: path.join(__dirname,outputDirectory)
  },
  resolve: {
    alias: {
      common: path.resolve(__dirname, "src/common"),
      components: path.resolve(__dirname, "src/components"),
      app_context: path.resolve(__dirname, "src/components/AppContext.js"),
    }
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /^(?!.*?\.module).*\.css$/,
        use: ['style-loader', 'css-loader']
      },
      {
        test: /\.module\.css$/,
        use: ['style-loader', {
          loader: 'css-loader',
          options: {
            modules: true
          }
        }]
      }
    ]
  },
  devServer: {
    port: 3000,
  },
  devtool: "cheap-module-source-map",
};
