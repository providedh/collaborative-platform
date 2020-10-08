import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars

export default function Menu ({projectId, focused, configuration}) {
  if (focused === null) {return ''}
  return (<div className={styles.menu}>
    <div className={styles.container}>
      <ul className="list-group list-group-horizontal">
        <li className="list-group-item">
          <button type="button" className="btn btn-outline-success">Unify</button>
        </li>
        <li className="list-group-item">
          <b>Confidence</b><br/> {Math.trunc(+focused.degree)}%
        </li>
        <li className="list-group-item">
          <button type="button" className="btn btn-outline-danger">Reject</button>
        </li>
      </ul>
    </div>
    <hr/>
  </div>)
}

Menu.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
