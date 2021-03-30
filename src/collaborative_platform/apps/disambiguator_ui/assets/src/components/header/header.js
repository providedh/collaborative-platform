import React from 'react'
import PropTypes from 'prop-types'

import {JobManager} from '../jobManager'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

export default function Header ({projectName, projectId, projectVersion, ...restProps}) {
  return (
    <div className={styles.header + ' mb-3'}>
      <h1>{projectName} <span>Current version: </span><span className="text-muted">v{projectVersion}</span></h1>
      <b>Disambiguating entities through unifications</b>
      <JobManager projectId={projectId}/>
    </div>
  )
}

Header.propTypes = {
  projectId: PropTypes.string,
  projectName: PropTypes.string,
}
