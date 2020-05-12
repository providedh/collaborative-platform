import React from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'
import TabContainer from '../TabContainer'

export default function SidePanel ({ title, labels, onClose = null, display, children }) {
  return (
    <div className={styles.sidePanel + (display === true ? '' : ' d-none')}>
      <div className={styles.header}>
        <h5>{title}</h5>
        {onClose == null ? ''
          : <button type="button"
            className="close mr-4 mt-4"
            aria-label="Close"
            onClick={onClose}>
            <span aria-hidden="true">&times;</span>
          </button>}
      </div>
      <hr className="hr"/>

      <TabContainer labels={labels}>
        {children}
      </TabContainer>
    </div>
  )
}

SidePanel.propTypes = {
  title: PropTypes.string,
  labels: PropTypes.array,
  onClose: PropTypes.func,
  display: PropTypes.bool,
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node
  ])
}
