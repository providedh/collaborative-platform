import React from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars

export default function Header ({projectName, ...restProps}) {
  console.log(restProps)
  return (
    <div className={styles.header}>
      <h1>{projectName}</h1>
    </div>
  )
}

Header.propTypes = {
  projectId: PropTypes.string,
  projectName: PropTypes.string,
}
