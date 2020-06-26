import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { ActionType, ActionTarget, ActionObject, AtomicActionBuilder, TEIentities } from 'common/types'

import { WithAppContext } from 'common/context/app'

export default function CreateAttributeWithContext (props) {
  return (
    <WithAppContext>
      <CreateAttribute {...props}/>
    </WithAppContext>
  )
}

function onAttributeDelete (id, property) {
  const builder = AtomicActionBuilder(ActionTarget.entity, ActionType.delete, ActionObject.property)
  const action = builder(id, property)
  alert(JSON.stringify(action))
}

function onAttributeChange (id, property, value, edit) {
  const builder = AtomicActionBuilder(ActionTarget.entity, ActionType.modify, ActionObject.property)
  const action = builder(id, property, value)
  alert(JSON.stringify(action))
  edit(null)
}

function onAttributeAdd (id, property, value) {
  const builder = AtomicActionBuilder(ActionTarget.entity, ActionType.add, ActionObject.property)
  const action = builder(id, [{ property, value }])
  alert(JSON.stringify(action))
}

function CreateAttribute (props) {
  const entityType = TEIentities[props.entity.type]

  const presentAttributes = new Set(props.entity.properties.map(x => x.name))
  const freeAttributes = entityType.properties
    .filter(x => !presentAttributes.has(x))

  const [attributeName, setAttributeName] = useState(freeAttributes[0])
  const [attributeValue, setAttributeValue] = useState('')
  const [visible, show] = useState(false)
  const [editingAttribute, edit] = useState(null)

  const attributeItems = props.entity.properties.map((attribute, i) =>
    <li key={i}>
      <span className={attribute.saved === false ? 'text-danger' : 'd-none'}>
        (unsaved)
        <button type="button"
          onClick={() => onAttributeDelete(props.entity['xml:id'], attribute.name)}
          className="btn btn-sm btn-link p-0 mx-1 text-danger"><u> -delete</u></button>
        <button type="button"
          onClick={() => edit({ ...attribute })}
          className="btn btn-sm btn-link p-0 mx-1 text-info"><u> *edit</u></button>
      </span>
      <span>{attribute.name} : </span>
      <span> {attribute.value}</span>
    </li>)

  const attributeOptions = freeAttributes.map(x => <option key={x} value={x}>{x}</option>)

  return <div>
    <span>Attributes</span>
    <ul className={(visible === false && editingAttribute === null) ? 'mb-1' : 'd-none'}>
      {attributeItems}
    </ul>
    <div className={freeAttributes.length === 0 ? 'd-none' : ''}>
      <form className={(editingAttribute !== null || visible === false) ? 'd-none' : 'p-2 rounded'} style={{ backgroundColor: 'rgba(0,0,0,.03)' }}>
        <div className="row">
          <div className="col">
            <div className="form-group">
              <label htmlFor="attribute">Attribute</label>
              <select className="form-control form-control-sm"
                value={attributeName}
                onChange={e => setAttributeName(e.target.value)}
                id="attribute">
                {attributeOptions}
              </select>
            </div>
          </div>
          <div className="col">
            <label htmlFor="value">Value</label>
            <input type="text"
              value={attributeValue}
              onChange={e => setAttributeValue(e.target.value)}
              className="form-control form-control-sm"
              id="value"
              placeholder="Attribute value ..."/>
          </div>
        </div>
        <div className="row mt-2">
          <div className="col">
            <button type="button btn-sm"
              onClick={() => onAttributeAdd(props.entity['xml:id'], attributeName, attributeValue)}
              className="btn btn-sm btn-outline-primary">Add attribute</button>
          </div>
        </div>
      </form>
    </div>
    <form className={editingAttribute === null ? 'd-none' : 'p-2 rounded'} style={{ backgroundColor: 'rgba(0,0,0,.03)' }}>
      <div className="row">
        <div className="col">
          <label htmlFor="value">{editingAttribute?.name}</label>
          <input type="text"
            className="form-control form-control-sm"
            onChange={e => edit({ name: editingAttribute?.name, value: e.target.value })}
            value={editingAttribute === null ? '' : editingAttribute.value}/>
        </div>
      </div>
      <div className="row mt-2">
        <div className="col">
          <button type="button btn-sm"
            onClick={() => onAttributeChange(props.entity['xml:id'], editingAttribute.name, editingAttribute.value, edit)}
            className="btn btn-sm btn-outline-primary">Modify</button>
        </div>
      </div>
    </form>
    <div className={freeAttributes.length === 0 ? 'd-none' : ''}>
      <button className="btn btn-link btn-sm"
        type="button"
        onClick={() => show(!visible)}>
        {visible === true ? 'Cancel' : '+ Add attribtue'}
      </button>
    </div>
    <div className={editingAttribute === null ? 'd-none' : ''}>
      <button className="btn btn-link btn-sm"
        type="button"
        onClick={() => edit(null)}>
        Cancel
      </button>
    </div>
    <hr className="mt-0"/>
  </div>
}

CreateAttribute.propTypes = {
  entity: PropTypes.shape({
    type: PropTypes.string,
    'xml:id': PropTypes.string,
    properties: PropTypes.array
  }),
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    entities: PropTypes.object,
    configuration: PropTypes.object
  })
}
