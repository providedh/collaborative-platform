import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars

function capitalize(text){
  return text[0].toLocaleUpperCase() +
    text.slice(1).toLocaleLowerCase()
}

function EntityName({entity, focused, projectId, setEntity, configuration}) {
  const name = entity.type + '-' + entity.id
  const targetName = focused.type + '-' + focused.id
  const isSelected = (entity.file_id+name) === (focused.file_id+targetName)
  const iconCode = configuration.entities[entity.type].icon;
  const annotatorURL =
    `/close_reading/project/${projectId}/file/${entity.file_id}/`

  const cssClasses = [
    styles.entityName,
    isSelected === false ? '' : styles.isSelected
  ].join(' ')

  return <div
      onClick={() => setEntity(entity)}
      className={cssClasses}>
    <span className={styles.filename}>
      {entity.file_name}
      <a target="new" href={annotatorURL}><i className="fas fa-external-link-alt"></i></a>
    </span>
    <span className={styles.slash}>/</span>
    <span className={styles.entity}>
      <i className="fas" data={iconCode}></i> {name}
    </span>
  </div>
}

export default function TargetDescription ({
    entity,
    projectId,
    configuration,
    targetIsClique,
    cliqueName='',
    entities,
    setEntity}) {
  if (entity === null) {return ''}

  const entityNames = entities.map((e, i) =>
    <EntityName key={i} {...{entity: e, focused: entity, setEntity, projectId, configuration}}/>)

  const properties = Object
    .entries(entity.properties)
    .map((p, i) => (
      <span key={i} className={styles.property}>
        <i>{capitalize(p[0])}</i>: {p[1]}
      </span>))

  const nameContainerCssClasses = [
    'd-flex',
    targetIsClique === false ? '' : styles.clique
  ].join(' ')

  return (<div className={styles.target}>
    <div className={nameContainerCssClasses}>
      <span className={targetIsClique === false ? 'd-none' : styles.cliqueName}>
        {cliqueName}
      </span>
      <div>
        {entityNames}
      </div>
    </div>
    <div className={targetIsClique === false ? 'd-none' : ''}>
      <p className="my-3">
        A clique is a group of unified entities.<br/>
        Toggle the entity shown by clicking another one above.
      </p>
      <EntityName {...{entity, focused: entity, setEntity: null, projectId, configuration}}/>
    </div>
    <p>
      {properties}
    </p>
  </div>)
}

TargetDescription.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
