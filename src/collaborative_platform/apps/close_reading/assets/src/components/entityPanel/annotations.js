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
import Annotation from './annotation.js'
import { saveOperations, discardOperations} from 'common/helpers'
import {onDeleteClick, onDiscard, onSave, onCreate, onModify} from './annotationActionHelpers.js'

export default function CreateAnnotationWithContext (props) {
  return (
    <WithAppContext>
      <CreateAnnotation {...props}/>
    </WithAppContext>
  )
}

function CreateAnnotation (props) {
  const [visible, show] = useState(false)
  const [editingAnnotation, edit] = useState(null)

  console.log(props.entity.annotations)

  const annotationItems = props.entity.annotations.map((annotation, i) =>
    <Annotation key={i} annotation={annotation} {...props}/>)

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
