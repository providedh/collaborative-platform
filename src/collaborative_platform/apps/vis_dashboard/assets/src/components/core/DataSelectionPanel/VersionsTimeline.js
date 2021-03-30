import React from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'
import { WithAppContext } from 'app_context'

export default function ProjectVersionTimelineWithContext (props) {
  return (
    <WithAppContext>
      <ProjectVersionTimeline {...props}/>
    </WithAppContext>
  )
}

function ProjectVersionTimeline ({ selected, context, onChange }) {
  const timestamp = (v, i) => (
    <div key={i}
      className={`d-flex ${styles.timestamp} ${+v.version <= +selected.version ? styles.selected : ''}`}
      onClick={() => onChange(v)}>
      <span className={`border ${styles.icon}`}/>
      <div className="pl-3">
        <h6 className="pl-0">{v.date.toUTCString()}</h6>
        {v.files.length} Commits in this project version by {[...new Set(v.files.map(x => x.author))].join(', ')}
      </div>
    </div>
  )

  return (
    <div className={styles.timeline}>
      <span className={styles.timeBar}>
        <span>Present day</span>
        <span/>
        <span style={{ height: (100 * context.projectVersions.length) + 'px' }}/>
        <span/>
        <span>Project creation</span>
      </span>
      {context.projectVersions.map((v, i) => timestamp(v, i))}
    </div>
  )
}

ProjectVersionTimeline.propTypes = {
  selected: PropTypes.shape({
    version: PropTypes.number
  }),
  context: PropTypes.shape({
    projectVersions: PropTypes.array
  }),
  onChange: PropTypes.func
}
