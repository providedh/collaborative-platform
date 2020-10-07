import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars

function capitalize(text){
  return text[0].toLocaleUpperCase() +
    text.slice(1).toLocaleLowerCase()
}

export default function Target ({entity, projectId, configuration}) {
  if (entity === null) {return ''}
  console.log(entity)

  const annotatorURL =
    `/close_reading/project/${projectId}/file/${entity.file_id}/`

  const properties = Object
    .entries(entity.properties)
    .map((p, i) => (
      <span key={i} className={styles.property}>
        <i>{capitalize(p[0])}</i>: {p[1]}
      </span>))
  console.log(configuration)
  const iconCode = configuration.entities[entity.type].icon;

  return (<div className={styles.target}>
    <p>
      <span className={styles.filename}>
        {entity.file_name}
        <a target="new" href={annotatorURL}><i className="fas fa-external-link-alt"></i></a>
      </span>
      <span className={styles.slash}>/</span>
      <span className={styles.entity}>
        <i className="fas" data={iconCode}></i> {entity.type + '-' + entity.id}
      </span>
      {properties}
    </p>
  </div>)
}

Target.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
