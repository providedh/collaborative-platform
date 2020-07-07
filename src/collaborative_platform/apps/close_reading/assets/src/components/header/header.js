import React from 'react'
import PropTypes from 'prop-types'

import { WithAppContext } from 'common/context/app'
import { SaveButton } from 'components/saveButton'
import styles from './header.module.css'

export default function HeaderWithContext (props) {
  return (
    <WithAppContext>
      <Header {...props}/>
    </WithAppContext>
  )
}

function Header (props) {
  return <div className={styles.header}>
    <div className={styles.top}>
      <div className={styles.fileName}>
        <h1>
          {props.fileName}
        </h1>
        <h2 className="font-weight-light">
          Version {props.fileVersion}
        </h2>
      </div>
      <SaveButton/>
    </div>
  </div>
}

Header.propTypes = {
  fileName: PropTypes.string,
  fileVersion: PropTypes.string
}
