import React, {useState, useEffect} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars
import {EntityName, CliqueName} from 'common/components'

const updateTimeDelays = [
  500,
  1000,
  2500,
  5500,
]

function updateUnsavedOperations(projectId, setUnsavedOperations) {
  API.getUnsavedUnifications(projectId).then(json => {
    const unsaved = json?.uncommitted_changes?.unifications_to_add
    if (unsaved !== undefined) {
      setUnsavedOperations(unsaved)
    }
  })
}

function periodicUpdate(projectId, setUnsavedOperations, waitTimes, setWaitTimes) {
  if (waitTimes.length === 0) {return}
  (new Promise((resolve, reject) => { // ensures that no update will interfere
    setWaitTimes([])
    resolve(waitTimes)
  })).then(times => {
    times.map(tsp => setTimeout(() => updateUnsavedOperations(projectId, setUnsavedOperations), tsp))  
  })
}

function saveUncommitedChanges(projectId, waitTimes, setWaitTimes) {
  API.saveUnifications(projectId).then(() => {
    scheduleCommitUpdates(projectId, waitTimes, setWaitTimes)
  })
}

function scheduleCommitUpdates(projectId, waitTimes, setWaitTimes) {
  const newWaitTimes = [...waitTimes, ...updateTimeDelays]
  newWaitTimes.sort((a, b) => a-b)
  setWaitTimes(newWaitTimes)
}

export default function Button ({projectId, assertFlag, configuration}) {
  const [visible, setVisibility] = useState(false)
  const [unsavedOperations, setUnsavedOperations] = useState([])
  const [waitTimes, setWaitTimes] = useState([])

  periodicUpdate(projectId, setUnsavedOperations, waitTimes, setWaitTimes)
  useEffect(() => {
    scheduleCommitUpdates(projectId, waitTimes, setWaitTimes)
  }, [assertFlag])
  window.API = API

  const cssClasses = [
    styles.button,
    visible === false ? styles.collapsed : styles.visible
  ].join(' ')

  const buttonCssClasses = [
    'btn',
    unsavedOperations.length === 0 ? 'btn-outline-primary' : 'btn-primary'
  ].join(' ')

  const tooltipCssClasses = [
    'list-group',
    styles.operations,
    unsavedOperations.length === 0 ? 'd-none' : ''
  ].join(' ')

  const arrowCssClasses = [
    styles.arrow,
    unsavedOperations.length === 0 ? 'd-none' : ''
  ].join(' ')

  const msg = unsavedOperations.length === 0
    ? 'No operations to save'
    : `Save ${unsavedOperations.length} unifications`

  const operations = unsavedOperations.map((x, i) =>
    <li key={i} className="list-group-item">
      <div className="text-nowrap">
        <span className="d-inline-flex">
          <EntityName {...{configuration, entity: {
            type: x.entity_type,
            'xml:id': x['entity_xml-id'],
            file_name: x.entity_file_name
          }}}/>
        </span> ⇨ <span>Clique {x.clique_id} {x.clique_name.length > 0 ? `(${x.clique_name})` : ''}</span>
      </div>
      ({x.certainty} certainty)
    </li>)

  return (<div className={cssClasses}>
    <button
      type="button"
      onClick={unsavedOperations.length === 0 ? null : () => saveUncommitedChanges(projectId, waitTimes, setWaitTimes)}
      className={buttonCssClasses} disabled={unsavedOperations.length === 0}>
      {msg}
    </button>
    <div className={arrowCssClasses}/>
    <div className={tooltipCssClasses}>
      <ul className="pl-0">
        {operations}
      </ul>
    </div>
  </div>)
}

Button.propTypes = {
  projectId: PropTypes.string,
}
