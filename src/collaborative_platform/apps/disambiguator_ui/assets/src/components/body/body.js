import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars
import { TargetDescription } from 'components/targetDescription'

export default function Body ({projectId, focused, configuration}) {
  if (focused === null) {return ''}
  console.log(focused)
  return (<div className={styles.body}>
    <TargetDescription {...{projectId, configuration, entity: focused.entity}} />
  </div>)
}

Body.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
