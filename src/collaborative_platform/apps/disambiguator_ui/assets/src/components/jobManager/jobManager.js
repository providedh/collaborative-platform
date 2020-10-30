import React, {useState, useEffect} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

const fetchPeriod = 1000 * 60 * 2

function periodicJobFetch(projectId, setJobs) {
  fetchJobs(projectId, setJobs)
  setTimeout(() => periodicJobFetch(projectId, setJobs), fetchPeriod)
}

function fetchJobs(projectId, setJobs) {
  API.getDisambiguatorStatus(projectId)
    .then((jobs) => {
      setJobs(jobs.sort((a, b) => new Date(b.created) - new Date(a.created)));
    })
    .catch(err => console.error('Failed to retrieve jobs for project ' + projectId))
}

function startAnalysis(projectId, setJobs) {
  API.updateDisambiguatorStatus(projectId, {}, {action: 'start'})
    .then(() => {
      setTimeout(() => fetchJobs(projectId, setJobs), 500)
    })
    .catch(err => console.error('Failed to start analysis job for project ' + projectId, err))
}

function abortAnalysis(projectId, setJobs) {
  API.updateDisambiguatorStatus(projectId, {}, {action: 'abort'})
    .then(() => {
      fetchJobs(projectId, setJobs)
    })
    .catch(err => console.error('Failed to abort analysis job for project ' + projectId, err))
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

function JobAction({job, setJobs, projectId}) {
  let action = ''
  if (['Queued', '_Started', '_Running'].includes(job?.status)) {
    action = (
      <button
          type="button"
          onClick={() => abortAnalysis(projectId, setJobs)}
          className="btn ml-3 btn-outline-danger">
        Abort analysis
      </button>
    )
  } else if ([undefined, 'Finished', 'Aborted', 'Failed'].includes(job?.status)) {
    action = (
      <button
          type="button"
          onClick={() => startAnalysis(projectId, setJobs)}
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
  useEffect(() => {periodicJobFetch(projectId, setJobs)}, [])

  return (<div className={styles.jobs}>
    <div className="d-flex">
      <JobStatus job={jobs.length === 0 ? null : jobs[0]}/>
      <JobAction projectId={projectId} setJobs={setJobs} job={jobs.length === 0 ? null : jobs[0]}/>
    </div>
    <button
      type="button"
      className={historyShown ? 'd-none' : styles.showHistory + " btn btn-link"}
      onClick={() => setHistoryVisibility(true)}>Show analysis history </button>
    <div className={historyShown ? '' : ' d-none'}>
      <div className="d-flex align-items-center justify-content-between">
        <span className="text-muted">Most recent first</span>
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
