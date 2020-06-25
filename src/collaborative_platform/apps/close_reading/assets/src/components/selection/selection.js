import React from 'react'
import { WithAppContext } from 'common/context/app'
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
