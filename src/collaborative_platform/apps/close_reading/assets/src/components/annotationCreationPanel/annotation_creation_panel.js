import React from 'react'
import PropTypes from 'prop-types'

import { WithAppContext } from 'common/context/app'
import styles from './annotation_creation_panel.module.css'

export default function AnnotationCreationPanelWithContext (props) {
  return (
    <WithAppContext>
      <AnnotationCreationPanel {...props}/>
    </WithAppContext>
  )
}

function AnnotationCreationPanel (props) {
  return <div className={styles.annotationCreationPanel}>

  </div>
}

AnnotationCreationPanel.propTypes = {
  selection: PropTypes.shape({
    type: PropTypes.string,
    target: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(PropTypes.number)
    ]),
    screenX: PropTypes.number,
    screenY: PropTypes.number
  })
}
