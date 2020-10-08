import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars
import { TargetView } from 'components/targetView'
import { AssertMenu } from 'components/assertMenu'

export default function Body ({projectId, focused, configuration}) {
  if (focused === null) {return ''}

  const {entity, target_entity, target_clique} = focused
  const targetIsClique = target_entity === undefined && target_clique !== undefined
  const target = targetIsClique === true ? target_clique : target_entity

  return (<div className={styles.body}>
    <AssertMenu {...{projectId, focused, configuration}}/>
    <div className={styles.viewContainer}>
      <TargetView {...{projectId, configuration, target: entity}} />
      <TargetView {...{projectId, configuration, targetIsClique, target}} />
    </div>
  </div>)
}

Body.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
