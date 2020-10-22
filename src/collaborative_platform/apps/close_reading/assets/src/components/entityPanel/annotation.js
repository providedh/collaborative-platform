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

function AnnotationDescription ({annotation, props}) {
  const annotationCategories = 
    x => x.split(' ').map(x => x.split('#')[1]).join(', ')

  if (annotation.isUnification === true) {
    return <React.Fragment>
      <span>{authorName(annotation.resp, props.context.user, props.context.authors)}</span>
      <span> accepted the automatic unification (<span className="text-primary">{annotation.degree}</span> algorithmic confidence) with </span>
      <span className="text-primary">{annotation.assertedValue} </span>
      with <span className="text-primary">{annotation.cert} {annotationCategories(annotation.ana)}</span> certainty.
      <span className={annotation?.desc?.length > 0 ? 'text-primary' : 'd-none'}>
        <br/><b>&quot;</b><i>{annotation.desc}</i><b>&quot;</b>
      </span>
    </React.Fragment>
  }

  return <React.Fragment>
    {annotation.status !== OperationStatus.edited ? ''
      : <del className="text-muted">
        {authorName(annotation.prev.resp, props.context.user, props.context.authors) + ' '}
        marked with {annotation.prev.cert} {annotationCategories(annotation.prev.ana)} certainty: that the {annotation.prev.locus + ' '}
        <span className={annotation.prev?.match?.length > 0 ? '' : 'd-none'}> of {annotation.prev.match + ' '} </span>
        should be {annotation.prev.assertedValue}.
        <span className={annotation.prev?.desc?.length > 0 ? '' : 'd-none'}>
          <br/><b>&quot;</b><i>{annotation.prev.desc}</i><b>&quot;</b>
        </span>
      </del>
    }

    <span>{authorName(annotation.resp, props.context.user, props.context.authors)}</span>
    <span> marked with </span>
    <span className="text-primary">{annotation.cert} {annotationCategories(annotation.ana)}</span>
    <span> certainty: that the </span>
    <span className="text-primary">{annotation.locus}</span>
    <span className={annotation?.match?.length > 0 ? '' : 'd-none'}> of <span className="text-primary">{annotation.match}</span></span>
    <span> should be </span>
    <span className="text-primary">{annotation.assertedValue}.</span>
    <span className={annotation?.desc?.length > 0 ? 'text-primary' : 'd-none'}>
      <br/><b>&quot;</b><i>{annotation.desc}</i><b>&quot;</b>
    </span>
  </React.Fragment>
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