import React from 'react'
import PropTypes from 'prop-types'

import styles from './selection.css'

export default function SelectionWithContext (props) {
    return (
      <WithAppContext>
        <Selection {...props}/>
      </WithAppContext>
    )
  }

function Selection (props) {
    return <div className={styles.selection}>

    </div>
}

Selection.propTypes = {}