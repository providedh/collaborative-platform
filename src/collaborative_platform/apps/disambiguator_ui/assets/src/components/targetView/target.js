import React, {useState, useEffect} from 'react'
import PropTypes from 'prop-types'

import {TargetDescription} from 'components/targetDescription'
import {TargetPreview} from 'components/targetPreview'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

function useEntities(target, targetIsClique) {
  let entities

  if (targetIsClique) {
    entities = target.entities
  } else {
    entities = [target]
  }

  const [entity, setEntity] = useState(entities[0])

  useEffect(() => {
    setEntity(entities[0])
  }, [target])

  return [entities, entity, setEntity]
}

export default function Target ({target, projectId, configuration, targetIsClique=false}) {
  if (target === null) {return ''}

  const [entities, entity, setEntity] = useEntities(target, targetIsClique)
  //console.log(target, targetIsClique, entity, entities)

  return (<div className={styles.targetView}>
      <TargetDescription {...{
        projectId,
        configuration,
        entity,
        targetIsClique,
        cliqueName: target?.name || '',
        entities,
        setEntity}} />
      <TargetPreview {...{projectId, configuration, entity}} />
    </div>)
}

Target.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
