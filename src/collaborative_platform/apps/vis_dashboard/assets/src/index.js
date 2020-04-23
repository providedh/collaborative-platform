import React from 'react'
import { render } from 'react-dom'
import App from './components/App'

const dashboardConfig = (Object.hasOwnProperty.call(window, 'config') && Object.keys(window.config).length > 0)
  ? Object.assign({ views: [], layout: [], authors: [], currentVersion: null }, window.config)
  : null

render(<App savedConf={dashboardConfig} />, document.getElementById('react-root'))
