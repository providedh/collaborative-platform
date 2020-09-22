import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars

export default function Navigation ({currentIndex, setIndex, unifications, ...restProps}) {
  const [listShown, setListVisibility] = useState([])

  const navigationCssClasses = [
    'd-flex',
    'position-relative',
    'container-fluid',
    'flex-row',
    'justify-content-between',
    styles.navigation
  ].join(' ')

  const navButtonCssClasses = [
    styles.navButton,
    'btn',
    'btn-link'
  ].join(' ')

  return (<React.Fragment>
    <div className={navigationCssClasses}>
      <button
          onClick={() => setIndex(Math.max(0, currentIndex-1))}
          type="button"
          className={navButtonCssClasses}>
        <span>⟵</span> <p className="d-inline m-0 p-0">Previous unification</p>
      </button>
      <div className={styles.listToggle}>
        <b>{Math.min(currentIndex + 1, unifications.length)} / {unifications.length}</b>
        <button
          onClick={() => setListVisibility(!listShown)}
          type="button"
          className={navButtonCssClasses}>
        <span>‣</span>
      </button>
      </div>
      <button
          onClick={() => setIndex(Math.min(unifications.length-1 , currentIndex+1))}
          type="button"
          className={navButtonCssClasses}>
        <p className="d-inline m-0 p-0">Next unification</p> <span>⟶</span>
      </button>
    </div>
    <hr className="mt-0 mx-4" style={{backgroundColor: 'var(--blue)'}}/>
  </React.Fragment>)
}

Navigation.propTypes = {
  currentIndex: PropTypes.number,
  setIndex: PropTypes.func,
}
