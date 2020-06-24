import React, {useState} from 'react'
import PropTypes from 'prop-types'

import {TEIentities} from 'common/types'
import {WithAppContext} from 'common/context/app'
import styles from './entity_creation_panel.module.css'

export default function EntityCreationPanelWithContext (props) {
  return (
    <WithAppContext>
      <EntityCreationPanel {...props}/>
    </WithAppContext>
  )
}

function capitalized (s) {
  return s[0].toUpperCase() + s.slice(1)
}

function EntityCreationPanel (props) {
  const entities = props.context.configuration.entities
  const [entity, setEntity] = useState(Object.keys(entities)[0])
  const entityType = Object.hasOwnProperty.call(TEIentities, entity)
      ?TEIentities[entity]
      :TEIentities['default']
  const [attributes, setAttributes] = useState(Object.fromEntries(entityType.properties.map(x => [x, ''])))

  function handleEntityChange(name) {
    setEntity(name)
    const entityType = Object.hasOwnProperty.call(TEIentities, name)
      ?TEIentities[name]
      :TEIentities['default']
    setAttributes(Object.fromEntries(entityType.properties.map(x => [x, ''])))
  }

  const attributeFields = Object.entries(attributes).map(([name, value]) => <div className="form-group col-4" key={name}>
    <label htmlFor={name}>{name}</label>
    <input type="text" 
           className="form-control form-control-sm" 
           id={name} 
           value={value} 
           onChange={e => setAttributes(Object.assign({}, attributes, {[name]: e.target.value}))} />
    </div>)

  const entityOptions = Object.keys(entities).map(x => 
    <option key={x} value={x}>{x}</option>)

  return <div className={styles.entityCreationPanel}>
    <form>
      <div className="form-group">
        <label htmlFor="entityType">Entity type</label>
        <select className="form-control form-control-sm" id="entityType" value={entity} onChange={e => handleEntityChange(e.target.value)}>
          {entityOptions}
        </select>
      </div>
      <div className="row">
        {attributeFields}
        <div className="form-group col-4">
          <button className="btn btn-link btn-sm"
            type="button"
            aria-controls="collapse"></button>
        </div>
      </div>
      <div className="row">
        <div className="form-group col-4">
          <button className="btn btn-outline-primary btn-sm"
            onClick={() => props.callback(entity, attributes)}
            type="button">Create</button>
        </div>
      </div>
    </form>
  </div>
}

EntityCreationPanel.propTypes = {
}