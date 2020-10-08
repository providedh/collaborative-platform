import React, {useState} from 'react'
import PropTypes from 'prop-types'

import {TargetDescription} from 'components/targetDescription'
import {TargetPreview} from 'components/targetPreview'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

export default function Target ({entity, projectId, configuration}) {
  if (entity === null) {return ''}
  console.log(entity)

  const annotatorURL =
    `/close_reading/project/${projectId}/file/${entity.file_id}/`

return (<div className={styles.targetView}>
    <TargetDescription {...{projectId, configuration, entity}} />
    <TargetPreview {...{projectId, configuration, entity}} />
  </div>)
}

Target.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
