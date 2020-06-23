import React from 'react'
import PropTypes from 'prop-types'

import {WithAppContext} from 'common/context/app'
import styles from './entity_panel.module.css'
import Annotations from './annotations.js'
import Attributes from './attributes.js'

export default function EntityPanelWithContext (props) {
  return (
    <WithAppContext>
      <EntityPanel {...props}/>
    </WithAppContext>
  )
}

function EntityPanel (props) {
  
  const entitiesMap = {}
  Object.entries(props.context.entities)
    .forEach(([_, entityList]) => {
      entityList.forEach(entity => {
        entitiesMap[entity['xml:id']] = entity
      })
    })
  const entity = entitiesMap[props.selection.target]

  const style = props.context.configuration.entities[entity.type]
  const icon = style.icon

  return <div className={styles.entityPanel}>
    <div className="card">
      <div className="card-header">
        <span className={styles.icon} style={{color: style.color}} dataicon={icon}>
          <div dangerouslySetInnerHTML={{__html: icon}} />
        </span>
        <h5 className="d-inline"> {props.selection?.target} ({entity.type})</h5>
      </div>
      <div className="card-body">
        <Attributes entity={entity} />
        <Annotations entity={entity} />
      </div>
    </div>
  </div>
}

EntityPanel.propTypes = {
  selection: PropTypes.shape({
    type: PropTypes.string,
    target: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(PropTypes.number)
    ]),
    screenX: PropTypes.number,
    screenY: PropTypes.number
  })
}