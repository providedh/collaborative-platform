import React from 'react'
import PropTypes from 'prop-types'

import {
  WebsocketRequest,
  WebsocketRequestType,
  ActionType,
  ActionTarget,
  ActionObject,
  AtomicActionBuilder,
  OperationStatus
} from 'common/types'

import { WithAppContext } from 'common/context/app'

export default function AttributeWithContext (props) {
  return (
    <WithAppContext>
      <Attribute {...props}/>
    </WithAppContext>
  )
}

function onDelete (id, property, websocket) {
  const builder = AtomicActionBuilder(ActionTarget.entity, ActionType.delete, ActionObject.property)
  const action = builder(id, property)
  const request = WebsocketRequest(WebsocketRequestType.modify, [action])
  websocket.send(request)
}

function onDiscard (id, websocket) {
  const request = WebsocketRequest(WebsocketRequestType.discard, [id])
  websocket.send(request)
}

function onSave (id, websocket) {
  const request = WebsocketRequest(WebsocketRequestType.save, [id])
  websocket.send(request)
}

function AttributeOption (props) {
  const { onClick, classes, text } = props
  const className = 'btn btn-sm btn-link p-0 mx-1 ' + classes

  return <button type="button" onClick={e => {
    e.preventDefault()
    onClick(e)
  }} className={className}><u>{text}</u></button>
}

function Attribute (props) {
  const { attribute, entity, i, onEdit } = props

  return <li key={i} className={attribute.status === OperationStatus.unsaved ? 'text-muted' : ''}>
    <span className={attribute.status === OperationStatus.unsaved ? 'text-danger' : 'd-none'}>
        (unsaved)
      <AttributeOption classes="text-danger" text=" -discard" onClick={e => {
        const operation = props.context.operations.filter(x => (
          x.edited_element_id === entity.target.value &&
              x.element_type === 'entity_property' &&
              x.method === 'POST' &&
              x.operation_result === `${entity.target.value}/${attribute.name}`
        ))

        if (operation.length !== 1) { return }
        onDiscard(operation[0].id, props.context.websocket)
      }}/>
      <AttributeOption classes="text-info" text=" save" onClick={e => {
        const operation = props.context.operations.filter(x => (
          x.edited_element_id === entity.target.value &&
              x.element_type === 'entity_property' &&
              x.method === 'POST' &&
              x.operation_result === `${entity.target.value}/${attribute.name}`
        ))

        if (operation.length !== 1) { return }
        onSave(operation[0].id, props.context.websocket)
      }}/>
    </span>
    <span className={attribute.status === OperationStatus.saved ? 'text-danger' : 'd-none'}>
      <AttributeOption classes="text-danger" text=" -delete" onClick={e => {
        onDelete(entity.target.value, attribute.name, props.context.websocket)
      }}/>
      <AttributeOption classes="text-info" text=" *edit" onClick={e => {
        onEdit({ ...attribute })
      }}/>
    </span>
    <span className={attribute.status === OperationStatus.deleted ? 'text-danger' : 'd-none'}>
        (deleted)
      <AttributeOption classes="text-danger" text=" commit" onClick={e => {
        const operation = props.context.operations.filter(x => (
          x.edited_element_id === entity.target.value &&
              x.element_type === 'entity_property' &&
              x.method === 'DELETE' &&
              x.old_element_id === attribute.name
        ))

        if (operation.length !== 1) { return }

        onSave(operation[0].id, props.context.websocket)
      }}/>
      <AttributeOption classes="text-info" text=" restore" onClick={e => {
        const operation = props.context.operations.filter(x => (
          x.edited_element_id === entity.target.value &&
              x.element_type === 'entity_property' &&
              x.method === 'DELETE' &&
              x.old_element_id === attribute.name
        ))

        if (operation.length !== 1) { return }

        onDiscard(operation[0].id, props.context.websocket)
      }}/>
    </span>
    <span className={attribute.status === OperationStatus.edited ? 'text-danger' : 'd-none'}>
        (edited)
      <AttributeOption classes="text-danger" text=" save" onClick={e => {
        const operation = props.context.operations.filter(x => (
          x.edited_element_id === entity.target.value &&
              x.element_type === 'entity_property' &&
              x.method === 'PUT' &&
              x.old_element_id === attribute.name
        ))

        if (operation.length !== 1) { return }

        onSave(operation[0].id, props.context.websocket)
      }}/>
      <AttributeOption classes="text-info" text=" restore" onClick={e => {
        const operation = props.context.operations.filter(x => (
          x.edited_element_id === entity.target.value &&
              x.element_type === 'entity_property' &&
              x.method === 'PUT' &&
              x.old_element_id === attribute.name
        ))

        if (operation.length !== 1) { return }

        onDiscard(operation[0].id, props.context.websocket)
      }}/>
    </span>

    <span> {attribute.name} : </span>
    <span> {attribute.status === OperationStatus.edited ? <del>{attribute.prev}</del> : ''} {attribute.value}</span>
  </li>
}

AttributeOption.propTypes = {
  onClick: PropTypes.func,
  text: PropTypes.string,
  classes: PropTypes.string
}

Attribute.propTypes = {
  i: PropTypes.number,
  entity: PropTypes.shape({
    type: PropTypes.string,
    'xml:id': PropTypes.object,
    properties: PropTypes.array,
    id: PropTypes.object,
    target: PropTypes.object
  }),
  attribute: PropTypes.shape({
    name: PropTypes.string,
    value: PropTypes.string,
    status: PropTypes.string,
    prev: PropTypes.string
  }),
  onEdit: PropTypes.func,
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    configuration: PropTypes.object,
    websocket: PropTypes.object,
    operations: PropTypes.arrayOf(PropTypes.object)
  })
}
