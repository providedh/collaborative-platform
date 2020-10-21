import React from 'react'
import styles from './entity.module.css'

export default function EntityName({entity, configuration}) {
  const name = entity['xml:id']
  const iconCode = configuration.entities[entity.type].icon;
  
  return <div className={styles.entityName}>
    <span className={styles.filename}>
      {entity.file_name}
    </span>
    <span className={styles.slash}>/</span>
    <span className={styles.entity}>
      <i className="fas" data={iconCode}></i> {name}
    </span>
  </div>
}