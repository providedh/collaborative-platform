import React, { useState } from 'react'
import PropTypes from 'prop-types'

import {
  WebsocketRequest,
  WebsocketRequestType,
  ActionType,
  ActionTarget,
  ActionObject,
  AtomicActionBuilder,
  TEIentities
} from 'common/types'

import { WithAppContext } from 'common/context/app'
import Attribute from './attribute'

export default function AttributesWithContext (props) {
  return (
    <WithAppContext>
      <Attributes {...props}/>
    </WithAppContext>
  )
}

function onAttributeChange (id, property, value, edit, websocket) {
  const builder = AtomicActionBuilder(ActionTarget.entity, ActionType.modify, ActionObject.property)
  const action = builder(id, property, value)
  const request = WebsocketRequest(WebsocketRequestType.modify, [action])

  edit(null)
  websocket.send(request)
}

function onAttributeAdd (id, property, value, websocket) {
  const builder = AtomicActionBuilder(ActionTarget.entity, ActionType.add, ActionObject.property)
  const action = builder(id, property, value)
  const request = WebsocketRequest(WebsocketRequestType.modify, [action])
  websocket.send(request)
}

function Attributes (props) {
  const entityType = TEIentities[props.entity.type]

  const presentAttributes = new Set(props.entity.properties.map(x => x.name))
  const freeAttributes = entityType.properties
    .filter(x => !presentAttributes.has(x))

  const [attributeName, setAttributeName] = useState(freeAttributes[0])
  const [attributeValue, setAttributeValue] = useState('')
  const [visible, show] = useState(false)
  const [editingAttribute, edit] = useState(null)

  const attributeItems = props.entity.properties.map((attribute, i) =>
    <Attribute key={i} {...{ attribute, i, entity: props.entity, onEdit: edit }}/>)

  const attributeOptions = freeAttributes.map(x => <option key={x} value={x}>{x}</option>)

  return <div className={props.entity.type === 'text fragment' ? 'd-none' : ''}>
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
            <input
              type={!['when', 'death', 'birth'].includes(attributeName) ? 'text' : (attributeName === 'when' && props.entity.type === 'time' ? 'time' : 'date')}
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
              onClick={e => {
                e.preventDefault()
                onAttributeAdd(props.entity.target.value, attributeName, attributeValue, props.context.websocket)
              }}
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
            type={!['when', 'death', 'birth'].includes(attributeName) ? 'text' : (attributeName === 'when' && props.entity.type === 'time' ? 'time' : 'date')}
            onChange={e => edit({ name: editingAttribute?.name, value: e.target.value })}
            value={editingAttribute === null ? '' : editingAttribute.value}/>
        </div>
      </div>
      <div className="row mt-2">
        <div className="col">
          <button type="button btn-sm"
            onClick={e => {
              e.preventDefault()
              onAttributeChange(
                props.entity.target.value,
                editingAttribute.name,
                editingAttribute.value,
                edit,
                props.context.websocket
              )
            }}
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

Attributes.propTypes = {
  entity: PropTypes.shape({
    type: PropTypes.string,
    'xml:id': PropTypes.object,
    properties: PropTypes.array,
    id: PropTypes.object,
    target: PropTypes.object
  }),
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    configuration: PropTypes.object,
    websocket: PropTypes.object,
    operations: PropTypes.arrayOf(PropTypes.object)
  })
}
