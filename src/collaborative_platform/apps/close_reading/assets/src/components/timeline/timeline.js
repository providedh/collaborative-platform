import React from 'react'

import { WithAppContext } from 'common/context/app'
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
