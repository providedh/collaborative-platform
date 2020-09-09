import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

import { WithAppContext } from 'common/context/app'
import { TEIentities } from 'common/types'
import styles from './entity_selector.module.css'

export default function EntitySelectorWithContext (props) {
  return (
    <WithAppContext>
      <EntitySelector {...props}/>
    </WithAppContext>
  )
}

function capitalized (s) {
  return s[0].toUpperCase() + s.slice(1)
}

function getPayloadForOptions (entityType, ref, properties, usingRef) {
  const payload = {}

  if (usingRef === true) {
    payload.new_element_id = ref
    if (ref === '') {return}
  } else {
    const nonEmptyProperties = Object.fromEntries(
      Object.entries(properties).filter(([key, val]) => val.length > 0)
    )
    payload.parameters = {
      entity_type: entityType,
      entity_properties: nonEmptyProperties
    }
  }

  return payload
}

function EntitySelector (props) {
  const entityConfiguration = props.context.configuration.entities

  const [selectedEntity, setEntity] = useState(Object.keys(entityConfiguration)[0])
  const [usingRef, setUsingRef] = useState(false)
  const [ref, setRef] = useState('')

  const entityType = TEIentities[selectedEntity]
  const [attributes, setAttributes] = useState(Object.fromEntries(entityType.properties.map(x => [x, ''])))

  const entities = Object.values(
    Object.fromEntries(
      props.context.entities.map(x => [x.target.value, x])))

  useEffect(() => props.onChange(getPayloadForOptions(selectedEntity, ref, attributes, usingRef)), [])

  function handleEntityChange (name) {
    setEntity(name)
    const entityType = TEIentities[name]
    const attributes = Object.fromEntries(entityType.properties.map(x => [x, '']))
    setAttributes(attributes)
    props.onChange(getPayloadForOptions(name, ref, attributes, usingRef))
  }

  function handleAttributeChange (value) {
    setAttributes(value)
    props.onChange(getPayloadForOptions(selectedEntity, ref, value, usingRef))
  }

  function handleRefChange (value) {
    setRef(value)
    props.onChange(getPayloadForOptions(selectedEntity, value, attributes, usingRef))
  }

  function handleUsingRefChange (value) {
    setUsingRef(value)
    props.onChange(getPayloadForOptions(selectedEntity, ref, attributes, value))
  }

  const entityOptions = Object.keys(entityConfiguration).map(x =>
    <option key={x} value={x}>{capitalized(x)}</option>)

  const attributeFields = Object.entries(attributes).map(([name, value]) => <div className="form-group col-4" key={name}>
    <label htmlFor={name}>{name}</label>
    <input type="text"
      className="form-control form-control-sm"
      id={name}
      type={!['when', 'death', 'birth'].includes(name) ? 'text' : (name === 'when' && selectedEntity === 'time' ? 'time' : 'date')}
      value={value}
      onChange={e => handleAttributeChange(Object.assign({}, attributes, { [name]: e.target.value }))} />
  </div>)

  const style = props.context.configuration.entities[selectedEntity]
  const icon = style.icon

  const refList = entities
    .filter(x => x.type === selectedEntity)
    .map(x =>
      <button 
          key={x.target.value} 
          onClick={() => handleRefChange(x.target.value)} 
          type="button" 
          className={(x.target === ref ? 'bg-light text-body ' : 'text-black-50 ') + 'list-group-item list-group-item-action mb-0'}>
        <div className="d-flex w-100 justify-content-between">
          <h5 className="mb-1">
            <span className={styles.icon} style={{ color: style.color }} dataicon={icon}>
              <div dangerouslySetInnerHTML={{ __html: icon }} />
            </span>
            {x.target.value}
          </h5>
          <small className="text-muted">{x.type}</small>
        </div>
        <ul>
          {x.properties.map((p, i) => <li key={i}><b>{p.name}:</b>{p.value}</li>)}
        </ul>
      </button>)

  return <React.Fragment>
    <div className="row">
      <div className="form-group">
        <label htmlFor="entityType">Entity type</label>
        <select className="form-control form-control-sm" id="entityType" value={selectedEntity} onChange={e => handleEntityChange(e.target.value)}>
          {entityOptions}
        </select>
      </div>
    </div>
    <div className="row">
      <span className="mr-2">This is a new entity</span>
      <div className="custom-control custom-switch">
        <input
          type="checkbox"
          className="custom-control-input"
          id="useRef"
          value={usingRef}
          onChange={() => handleUsingRefChange(!usingRef)}/>
        <label className="custom-control-label" htmlFor="useRef">This refers to an existing entity</label>
      </div>
    </div>
    <div className={'row ' + (usingRef === true ? 'd-none' : '')}>
      {attributeFields}
    </div>
    <div className={'row ' + (usingRef === false ? 'd-none' : '')}>
      <div className="d-block w-100 mb-2">
        {ref === '' ? <span className="text-danger"><b>No entity selected yet.</b></span> : <span>Entity <b>{ref}</b> selected.</span>}
      </div>
      <div className="list-group flex-fill overflow-auto">
        {refList.length > 0 ? refList
          : <li className="list-group-item list-group-item-warning border-0">
            There are no <b>{selectedEntity}</b> entities in this document to select from.
          </li>
        }
      </div>
    </div>

  </React.Fragment>
}

EntitySelector.propTypes = {
  onChange: PropTypes.func,
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    entities: PropTypes.arrayOf(PropTypes.object),
    configuration: PropTypes.object,
    websocket: PropTypes.object
  })
}
