import React from 'react'
import PropTypes from 'prop-types'

import styles from './timeline.css'

export default function TimelineWithContext (props) {
    return (
      <WithAppContext>
        <Timeline {...props}/>
      </WithAppContext>
    )
  }

function Timeline (props) {
    return <div className={styles.timeline}>

    </div>
}

Timeline.propTypes = {}