import React, {useState, useEffect} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

export default function Button ({projectId, unsavedOperations}) {
  const [visible, setVisibility] = useState(false)

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
    <li key={i} className="list-group-item">Some operation {i}</li>)

  return (<div className={cssClasses}>
    <button type="button" className={buttonCssClasses} disabled={unsavedOperations.length === 0}>
      {msg}
    </button>
    <div className={arrowCssClasses}/>
    <ul className={tooltipCssClasses}>
      {operations}
    </ul>
  </div>)
}

Button.propTypes = {
  projectId: PropTypes.string,
}
