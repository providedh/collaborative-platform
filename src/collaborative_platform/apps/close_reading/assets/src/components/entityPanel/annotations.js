import React, { useState } from 'react'

import { ActionType, ActionTarget, ActionObject, AtomicActionBuilder } from 'common/types'
import {WithAppContext} from 'common/context/app'
import AnnotateForm from './annotate_form.js'

export default function CreateAnnotationWithContext (props) {
  return (
    <WithAppContext>
      <CreateAnnotation {...props}/>
    </WithAppContext>
  )
}

function onDeleteClick (id) {
  const builder = AtomicActionBuilder(ActionTarget.certainty, ActionType.delete, ActionObject.certainty)
  const action = builder(id)
  alert(JSON.stringify(action))
}

function onAnnotationCreate (id, values) {
  const { locus, ana, cert, assertedValue, desc } = values
  const builder = AtomicActionBuilder(ActionTarget.certainty, ActionType.add, ActionObject.certainty)
  const action = builder(id, locus, ana, cert, assertedValue, desc)
  alert(JSON.stringify(action))
}

function onAnnotationModify (id, oldValues, newValues, edit) {
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
  alert(JSON.stringify(actions))
  edit(null)
}

function authorName(resp, user, authors) {
  if (resp === user) {return 'I'}
  const author = authors.filter(x => x['xml:id'] === resp)[0]
  return `${author?.forename} ${author?.surname}`
}

function CreateAnnotation (props) {
  const [visible, show] = useState(false)
  const [editingAnnotation, edit] = useState(null)

  const annotations = props.context.annotations.filter(x => x.target.slice(1) === props.entity['xml:id'])
  const annotationItems = annotations.map((annotation, i) =>
    <li key={i}>
      <span className={annotation.saved === false ? 'text-danger' : 'd-none'}>
        (unsaved)
        <button type="button btn-sm"
          onClick={() => onDeleteClick(annotation['xml:id'])}
          className="btn btn-link p-0 mx-1 text-danger">
          <u> -delete</u>
        </button>
        <button type="button btn-sm"
          onClick={() => edit(annotation)}
          className="btn btn-link p-0 mx-1 text-info"><u> *edit</u></button>
      </span>
      <span>{authorName(annotation.resp, props.context.user, props.context.authors)}</span>
      <span> marked with </span>
      <span className="text-primary">{annotation.cert}</span>
      <span> certainty: that the </span>
      <span className="text-primary">{annotation.locus}</span>
      <span className={annotation.match.length === 0 ? 'd-none' : ''}> of <span className="text-primary">{annotation.match}</span></span>
      <span> should be </span>
      <span className="text-primary">{annotation.assertedValue}.</span>
      <span className={annotation.desc.length === 0 ? 'd-none' : 'text-primary'}>
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
          callback={form => onAnnotationCreate(props.entity['xml:id'], form)}/>
        : <AnnotateForm entity={props.entity}
          annotation={editingAnnotation}
          submitText="Modify"
          callback={form => onAnnotationModify(editingAnnotation['xml:id'], editingAnnotation, form, edit)}/>
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