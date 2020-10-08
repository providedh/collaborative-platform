import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars

export default function Navigation ({proposals, listIndex, buffSize, ids, setListIndex, focusedIndex, setFocusedIndex}) {
  const [listShown, setListVisibility] = useState(false)

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
          onClick={() => setFocusedIndex(Math.max(0, focusedIndex-1))}
          type="button"
          className={navButtonCssClasses}>
        <span>⟵</span> <p className="d-inline m-0 p-0">Previous unification</p>
      </button>
      <div className={styles.listToggle}>
        <b>{Math.min(focusedIndex + 1, proposals.length)} / {ids.length}</b>
        <button
          onClick={() => setListVisibility(!listShown)}
          type="button"
          className={navButtonCssClasses}>
        <span>‣</span>
      </button>
      </div>
      <button
          onClick={() => setFocusedIndex(Math.min(proposals.length-1 , focusedIndex+1))}
          type="button"
          className={navButtonCssClasses}>
        <p className="d-inline m-0 p-0">Next unification</p> <span>⟶</span>
      </button>
    </div>
    <hr className="my-0 mx-4" style={{backgroundColor: 'var(--blue)'}}/>
  </React.Fragment>)
}

Navigation.propTypes = {
  proposals: PropTypes.arrayOf(PropTypes.object),
  listIndex: PropTypes.number,
  setListIndex: PropTypes.func,
  focusedIndex: PropTypes.number,
  setFocusedIndex: PropTypes.func,
}
