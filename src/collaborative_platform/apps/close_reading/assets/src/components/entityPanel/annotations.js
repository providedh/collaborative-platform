import React, { useState } from 'react'
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
import AnnotateForm from './annotate_form.js'

export default function CreateAnnotationWithContext (props) {
  return (
    <WithAppContext>
      <CreateAnnotation {...props}/>
    </WithAppContext>
  )
}

function onDeleteClick (id, websocket) {
  const builder = AtomicActionBuilder(ActionTarget.certainty, ActionType.delete, ActionObject.certainty)
  const action = builder(id)
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

function onCreate (id, values, websocket) {
  const { locus, ana, cert, assertedValue, desc, match } = values
  const builder = AtomicActionBuilder(ActionTarget.certainty, ActionType.add, ActionObject.certainty)

  let action = builder(id, locus, ana, cert, assertedValue, desc)
  if (locus === 'attribute') {
    action = builder(`${id}/${match}`, 'value', ana, cert, assertedValue, desc)
  }

  const request = WebsocketRequest(WebsocketRequestType.modify, [action])
  websocket.send(request)
}

function onModify (id, oldValues, newValues, edit, websocket) {
  const builder = AtomicActionBuilder(ActionTarget.certainty, ActionType.modify, ActionObject.certainty)
  const actions = []
  Object.entries(oldValues).map(([key, value]) => {
    if (key === 'ana') {
      const categories = value
        .split(' ')
        .map(x => x.split('#')[1])
        .sort()
        .join(' ')

      if (categories !== newValues.ana.sort().join(' ')) {
        actions.push(builder(id, 'ana', newValues.ana))
      }
    } else {
      if (value !== newValues[key]) {
        actions.push(builder(id, key, newValues[key]))
      }
    }
  })
  // const action = builder(id, attributeName, attributeValue)
  const request = WebsocketRequest(WebsocketRequestType.modify, actions)
  websocket.send(request)
  edit(null)
}

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

function CreateAnnotation (props) {
  const [visible, show] = useState(false)
  const [editingAnnotation, edit] = useState(null)

  const annotationItems = props.entity.annotations.map((annotation, i) =>
    <li key={i}>
      <span className={annotation.status === OperationStatus.unsaved ? 'text-danger' : 'd-none'}>
        (unsaved)
        <AnnotationOption classes="text-danger" text=" -discard" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'POST' &&
            x.operation_result === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onDiscard(operation[0].id, props.context.websocket)
        }}/>
        <AnnotationOption classes="text-info" text=" save" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'POST' &&
            x.operation_result === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onSave(operation[0].id, props.context.websocket)
        }}/>
      </span>
      <span className={annotation.status === OperationStatus.deleted ? 'text-danger' : 'd-none'}>
        (deleted)
        <AnnotationOption classes="text-danger" text=" commit" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'DELETE' &&
            x.edited_element_id === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onSave(operation[0].id, props.context.websocket)
        }}/>
        <AnnotationOption classes="text-info" text=" restore" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'DELETE' &&
            x.edited_element_id === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onDiscard(operation[0].id, props.context.websocket)
        }}/>
      </span>
      <span className={annotation.status === OperationStatus.edited ? 'text-danger' : 'd-none'}>
        (edited)
        <AnnotationOption classes="text-danger" text=" discard" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'PUT' &&
            x.edited_element_id === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onDiscard(operation[0].id, props.context.websocket)
        }}/>
        <AnnotationOption classes="text-info" text=" save" onClick={e => {
          const operation = props.context.operations.filter(x => (
            x.element_type === 'certainty' &&
            x.method === 'PUT' &&
            x.edited_element_id === annotation['xml:id']
          ))

          if (operation.length !== 1) { return }
          onSave(operation[0].id, props.context.websocket)
        }}/>
      </span>
      <span className={annotation.status === OperationStatus.saved ? '' : 'd-none'}>
        <AnnotationOption classes="text-danger" text=" -delete" onClick={e => {
          onDeleteClick(annotation['xml:id'], props.context.websocket)
        }}/>
        <AnnotationOption classes="text-info" text=" *edit" onClick={e => {
          edit(annotation)
        }}/>
      </span>

      {annotation.status !== OperationStatus.edited ? ''
        : <del className="text-muted">
          {authorName(annotation.prev.resp, props.context.user, props.context.authors) + ' '}
          marked with {annotation.prev.cert} certainty: that the {annotation.prev.locus + ' '}
          <span className={annotation.prev?.match?.length > 0 ? '' : 'd-none'}> of {annotation.prev.match + ' '} </span>
          should be {annotation.prev.assertedValue}.
          <span className={annotation.prev?.desc?.length > 0 ? '' : 'd-none'}>
            <br/><b>&quot;</b><i>{annotation.prev.desc}</i><b>&quot;</b>
          </span>
        </del>
      }

      <span>{authorName(annotation.resp, props.context.user, props.context.authors)}</span>
      <span> marked with </span>
      <span className="text-primary">{annotation.cert}</span>
      <span> certainty: that the </span>
      <span className="text-primary">{annotation.locus}</span>
      <span className={annotation?.match?.length > 0 ? '' : 'd-none'}> of <span className="text-primary">{annotation.match}</span></span>
      <span> should be </span>
      <span className="text-primary">{annotation.assertedValue}.</span>
      <span className={annotation?.desc?.length > 0 ? 'text-primary' : 'd-none'}>
        <br/><b>&quot;</b><i>{annotation.desc}</i><b>&quot;</b>
      </span>
    </li>)

  return <div>
    <span className="d-block">Annotations</span>
    <ul className={(visible === true || annotationItems.length === 0 || editingAnnotation !== null) ? 'd-none' : ''}>
      {annotationItems}
    </ul>
    <div className={(visible === false && editingAnnotation === null) ? 'd-none' : ''}>
      {editingAnnotation === null
        ? <AnnotateForm entity={props.entity}
          submitText="Create annotation"
          callback={form => onCreate(props.entity.target.value, form, props.context.websocket)}/>
        : <AnnotateForm entity={props.entity}
          annotation={editingAnnotation}
          submitText="Modify"
          callback={form => onModify(editingAnnotation['xml:id'], editingAnnotation, form, edit, props.context.websocket)}/>
      }
    </div>
    {editingAnnotation === null
      ? <button className="btn btn-link btn-sm"
        type="button"
        onClick={() => show(!visible)}
        data-toggle="collapse"
        data-target="#collapse"
        aria-expanded="false"
        aria-controls="collapse">{visible === true ? 'Cancel' : '+ Add annotation'}</button>
      : <button className="btn btn-link btn-sm"
        type="button"
        onClick={() => edit(null)}
        data-toggle="collapse"
        data-target="#collapse"
        aria-expanded="false"
        aria-controls="collapse">Cancel</button>
    }
  </div>
}

AnnotationOption.propTypes = {
  onClick: PropTypes.func,
  text: PropTypes.string,
  classes: PropTypes.string
}

CreateAnnotation.propTypes = {
  entity: PropTypes.shape({
    deleted: PropTypes.bool,
    properties: PropTypes.arrayOf(
      PropTypes.shape({
        name: PropTypes.string,
        value: PropTypes.string,
        saved: PropTypes.bool,
        deleted: PropTypes.bool
      })
    ),
    annotations: PropTypes.arrayOf(PropTypes.object),
    status: PropTypes.string,
    resp: PropTypes.string,
    saved: PropTypes.bool,
    type: PropTypes.string,
    'xml:id': PropTypes.string,
    target: PropTypes.object
  }),
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    entities: PropTypes.arrayOf(PropTypes.object),
    configuration: PropTypes.object,
    operations: PropTypes.arrayOf(PropTypes.object),
    websocket: PropTypes.object
  })
}
