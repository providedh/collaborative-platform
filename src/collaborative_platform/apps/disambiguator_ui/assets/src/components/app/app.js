import React from 'react'
import PropTypes from 'prop-types'

import { Header } from 'components/header'
import styles from './app.module.css' // eslint-disable-line no-unused-vars
import defState from './def_state.js'

export default function App ({projectName, projectId, projectVersion, ...restProps}) {
  const appCssClasses = [
    'container',
    styles.app
  ].join(' ')

  return (
    <div className={appCssClasses}>
      <Header {...{projectName, projectId, projectVersion}}/>
    </div>
  )
}

App.propTypes = {
  savedConf: PropTypes.object,
  projectId: PropTypes.string,
  user: PropTypes.string,
  projectId: PropTypes.string,
  projectName: PropTypes.string,
  projectVersion: PropTypes.string,
  configuration: PropTypes.object
}
