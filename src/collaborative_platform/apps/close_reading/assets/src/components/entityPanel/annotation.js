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
import {onDeleteClick, onDiscard, onSave, onCreate, onModify} from './annotationActionHelpers.js'
import AnnotationDescription from './annotation_desc.js'
import styles from './entity_panel.module.css'

function authorName (resp, user, authors) {
  if (resp === user) { return 'I' }
  const match = authors.filter(x => x['xml:id'] === resp)

  if (match.length === 0) { return resp }

  return `${match[0]?.forename} ${match[0]?.surname}`
}

function AnnotationOption (props) {
  const { onClick, classes, text } = props
  const className = 'btn btn-sm btn-link p-0 mx-1 ' + classes

  return <button type="button" onClick={e => {
    e.preventDefault()
    onClick(e)
  }} className={className}><u>{text}</u></button>
}

export default function Annotation({annotation, ...props}) {
  const author = authorName(annotation.resp, props.context.user, props.context.authors);

  return (
    <li>
      <span className={(author === 'I' && annotation.status === OperationStatus.unsaved) ? 'text-danger' : 'd-none'}>
        (unsaved)
        <AnnotationOption classes="text-danger" text=" -discard" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'POST' &&
            x.operation_result === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onDiscard(props.context.operations, operation[0].id, props.context.websocket)
        }}/>
        <AnnotationOption classes="text-info" text=" save" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'POST' &&
            x.operation_result === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onSave(props.context.operations, operation[0].id, props.context.websocket)
        }}/>
      </span>
      <span className={(author === 'I' && annotation.status === OperationStatus.deleted) ? 'text-danger' : 'd-none'}>
        (deleted)
        <AnnotationOption classes="text-danger" text=" commit" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'DELETE' &&
            x.edited_element_id === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onSave([operation[0]], operation[0].id, props.context.websocket)
        }}/>
        <AnnotationOption classes="text-info" text=" restore" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'DELETE' &&
            x.edited_element_id === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onDiscard([operation[0]], operation[0].id, props.context.websocket)
        }}/>
      </span>
      <span className={(author === 'I' && annotation.status === OperationStatus.edited) ? 'text-danger' : 'd-none'}>
        (edited)
        <AnnotationOption classes="text-danger" text=" discard" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'PUT' &&
            x.edited_element_id === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onDiscard([operation[0]], operation[0].id, props.context.websocket)
        }}/>
        <AnnotationOption classes="text-info" text=" save" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'PUT' &&
            x.edited_element_id === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onSave([operation[0]], operation[0].id, props.context.websocket)
        }}/>
      </span>
      <span className={(author === 'I' && annotation.status === OperationStatus.saved) ? '' : 'd-none'}>
        <AnnotationOption classes="text-danger" text=" -delete" onClick={e => {
          onDeleteClick(annotation['xml:id'], props.context.websocket)
        }}/>
        <AnnotationOption classes="text-info" text=" *edit" onClick={e => {
          edit(annotation)
        }}/>
      </span>

      <AnnotationDescription {...{annotation, props}}/>
    </li>)
}

AnnotationOption.propTypes = {
  onClick: PropTypes.func,
  text: PropTypes.string,
  classes: PropTypes.string
}