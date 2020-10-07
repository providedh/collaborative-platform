import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars
import { TargetDescription } from 'components/targetDescription'

export default function Body ({projectId, focused}) {
  if (focused === null) {return ''}
  console.log(focused)
  return (<div className={styles.body}>
    <TargetDescription entity={focused.entity} projectId={projectId} />
  </div>)
}

Body.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
