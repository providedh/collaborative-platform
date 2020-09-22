import React from 'react'
import PropTypes from 'prop-types'

import { Header } from 'components/header'
import styles from './app.module.css' // eslint-disable-line no-unused-vars
import defState from './def_state.js'

export default function App (props) {
  console.log(props)  
  return (
    <Header
      projectName={props.projectName}
      projectId={props.projectId}
    />
  )
}

App.propTypes = {
  savedConf: PropTypes.object,
  projectId: PropTypes.string,
  user: PropTypes.string,
  projectId: PropTypes.string,
  projectName: PropTypes.string,
  configuration: PropTypes.object
}
