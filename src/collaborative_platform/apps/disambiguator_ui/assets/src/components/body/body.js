import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars
import { TargetView } from 'components/targetView'
import { AssertMenu } from 'components/assertMenu'

export default function Body ({projectId, focused, configuration}) {
  if (focused === null) {return ''}
  return (<div className={styles.body}>
    <AssertMenu {...{projectId, focused, configuration}}/>
    <div className={styles.viewContainer}>
      <TargetView {...{projectId, configuration, entity: focused.entity}} />
      <TargetView {...{projectId, configuration, entity: focused.target_entity}} />
    </div>
  </div>)
}

Body.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
