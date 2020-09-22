import React, {useState} from 'react'
import PropTypes from 'prop-types'

import { Header } from 'components/header'
import { Navigation } from 'components/navigation'
import styles from './app.module.css' // eslint-disable-line no-unused-vars
import defState from './def_state.js'

export default function App ({projectName, projectId, projectVersion, ...restProps}) {
  const [unifications, updateUnifications] = useState([])
  const [currentIndex, setIndex] = useState(0)

  const appCssClasses = [
    'container',
    styles.app
  ].join(' ')

  return (
    <div className={appCssClasses}>
      <Header {...{projectName, projectId, projectVersion}}/>
      <Navigation {...{unifications, currentIndex, setIndex}}/>
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
