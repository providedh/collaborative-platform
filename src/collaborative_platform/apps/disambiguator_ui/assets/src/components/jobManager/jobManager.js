import React, {useState, useEffect} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

const fetchPeriod = 1000 * 60 * 10

function useJobFetch(projectId, setJobs) {
  useEffect(() => {
    API.getDisambiguatorStatus(projectId)
      .then((a,b) => console.log(a, b))
      .catch(err => console.error('Failed to retrieve jobs for project ' + projectId))
    setTimeout(() => useJobFetch(projectId, setJobs), fetchPeriod)
  }, [])
}

function startAnalysis(projectId) {
  API.updateDisambiguatorStatus(projectId, {}, {action: 'start'})
    .then((a,b) => console.log(a, b))
    .catch(err => console.error('Failed to start analysis job for project ' + projectId))
}

function abortAnalysis(projectId) {
  API.updateDisambiguatorStatus(projectId, {}, {action: 'abort'})
    .then((a,b) => console.log(a, b))
    .catch(err => console.error('Failed to abort analysis job for project ' + projectId))
}

function JobStatus({job}) {
  const statusToMessage = {
    Queued: 'is pending.',
    Started: 'just started.',
    Running: 'is still running',
    Finished: 'successfuly finished.',
    Aborted: 'was aborted.',
    Failed: 'failed',
  }
  const title = job === null ? 'No analysis has run yet' : 'Last analysis ' + statusToMessage[job.status]
  const subtitle = job === null ? 'Run one to get unifications' : 'Scheduled on: ' + job.created

  const titleCssClasses = [
    styles.jobStatusTitle,
    styles?.[job?.status] || styles.Missing
  ].join(' ')

  return <div className="d-flex flex-column ">
    <span className={titleCssClasses}>{title}</span>
    <span className={styles.jobStatusSubtitle + ' text-muted'}>{subtitle}</span>
  </div>
}

function JobAction({job, projectId}) {
  let action = ''
  if (['Queued', '_Started', '_Running'].includes(job?.status)) {
    action = (
      <button
          type="button"
          onClick={() => abortAnalysis(projectId)}
          className="btn ml-3 btn-outline-danger">
        Abort analysis
      </button>
    )
  } else if ([undefined, 'Finished', 'Aborted', 'Failed'].includes(job?.status)) {
    action = (
      <button
          type="button"
          onClick={() => startAnalysis(projectId)}
          className="btn ml-3 btn-outline-primary">
        Run new analysis
      </button>
    )
  }

  return action
}

export default function Jobs ({projectId, ...restProps}) {
  const [jobs, setJobs] = useState([])
  const [historyShown, setHistoryVisibility] = useState(false)
  useJobFetch(projectId, setJobs)

  window.pushAction = status => setJobs(
    [...jobs, {status, id: jobs.length, created: '1999-10-' + jobs.length}]
  )

  return (<div className={styles.jobs}>
    <div className="d-flex">
      <JobStatus job={jobs.length === 0 ? null : jobs[jobs.length-1]}/>
      <JobAction projectId={projectId} job={jobs.length === 0 ? null : jobs[jobs.length-1]}/>
    </div>
    <button
      type="button"
      className={historyShown ? 'd-none' : styles.showHistory + " btn btn-link"}
      onClick={() => setHistoryVisibility(true)}>Show analysis history </button>
    <div className={historyShown ? '' : ' d-none'}>
      <div className="d-flex align-items-center justify-content-between">
        <span className="text-muted">Oldest first</span>
        <button
          type="button"
          className={styles.hideHistory + " btn btn-link"}
          onClick={() => setHistoryVisibility(false)}>Hide history </button>
      </div>
      <hr/>
      <div className={styles.historyList}>
        {jobs.map(job => <JobStatus key={job.id} job={job}/>)}
      </div>
    </div>
  </div>)
}

Jobs.propTypes = {
  projectId: PropTypes.string,
}
