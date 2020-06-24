import React from 'react'
import PropTypes from 'prop-types'

import { WithAppContext } from 'common/context/app'
import styles from './header.module.css'

export default function HeaderWithContext (props) {
  return (
    <WithAppContext>
      <Header {...props}/>
    </WithAppContext>
  )
}

function Header (props) {
  const {
    fileName,
    fileVersion
  } = props

  return <div className={styles.header}>
    <div className={styles.top}>
      <div className={styles.fileName}>
        <h1>
          {fileName}
        </h1>
        <h2 className="font-weight-light">
          Version {fileVersion}
        </h2>
      </div>
      <button type="button" className={styles.saveButton + ' btn btn-outline-primary'}>Save</button>
    </div>
  </div>
}

Header.propTypes = {
  fileName: PropTypes.string,
  fileVersion: PropTypes.string
}
