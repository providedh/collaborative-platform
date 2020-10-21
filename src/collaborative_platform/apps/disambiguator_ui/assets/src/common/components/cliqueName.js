import React from 'react'
import styles from './clique.module.css'

export default function CliqueName({clique, configuration}) {
  const name = 'clique ' + clique.name
  const iconCode = configuration.entities[clique.entities[0].type].icon;
  const files = new Set(clique.entities.map(d => d.file_id))

  return <div className={styles.entityName}>
    <span className={styles.filename}>
      {name}
    </span>
    <span className={styles.slash}>/</span>
    <span className={styles.entity}>
      <i className="fas" data={iconCode}></i> {clique.entities.length} entities in {files.size} files
    </span>
  </div>
}