import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars
import { TargetView } from 'components/targetView'

export default function Body ({projectId, focused, configuration}) {
  if (focused === null) {return ''}
  console.log(focused)
  return (<div className={styles.body}>
    <TargetView {...{projectId, configuration, entity: focused.entity}} />
    <TargetView {...{projectId, configuration, entity: focused.target_entity}} />
  </div>)
}

Body.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
