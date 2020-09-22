import React, {useState} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

const fetchPeriod = 1000 * 60 * 1

function useJobFetch(projectId, setJobs) {
  API.getDisambiguatorStatus(projectId)
    .then((a,b) => console.log(a. b))
    .catch(err => console.error('Failed to retrieve jobs for project ' + projectId))
  setTimeout(() => useJobFetch(projectId, setJobs), fetchPeriod)
}

export default function Jobs ({projectId, ...restProps}) {
  const [jobs, setJobs] = useState([])
  useJobFetch(projectId, setJobs)

  return (<div className={styles.jobs}></div>)
}

Jobs.propTypes = {
  projectId: PropTypes.string,
}
