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

function confidence(cert, degree){
  const nf = new Intl.NumberFormat('en-emodeng', {maximumFractionDigits: 2})

  if (cert !== null && degree != null) {
    return `${cert}(${nf.format(degree)})`
  } else if (cert != null) {
    return `${cert}`
  } else if (degree != null) {
    return `${nf.format(degree)}`
  } else {
    return 'unspecified'
  }
}

function AssertedValue({annotation}){
  if (annotation.assertedValue === null) {
    return <React.Fragment>
        my doubts regarding the {annotation.locus + ' '}
        <span className={annotation?.match?.length > 0 ? '' : 'd-none'}> of {annotation.match + ' '} </span>
    </React.Fragment>
  } else {
    return <React.Fragment>
        that the {annotation.locus + ' '}
        <span className={annotation?.match?.length > 0 ? '' : 'd-none'}> of {annotation.match + ' '} </span>
        should be {annotation.assertedValue}
    </React.Fragment>
  }
}

export default function AnnotationDescription ({annotation, props}) {
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
        marked with {confidence(annotation.prev.cert, annotation.prev.degree)} {annotationCategories(annotation.prev.ana)} certainty: <AssertedValue annotation={annotation.prev}/>.
        <span className={annotation.prev?.desc?.length > 0 ? '' : 'd-none'}>
          <br/><b>&quot;</b><i>{annotation.prev.desc}</i><b>&quot;</b>
        </span>
      </del>
    }

    <span>{authorName(annotation.resp, props.context.user, props.context.authors)}</span>
    <span> marked with </span>
    <span className="text-primary">{confidence(annotation.cert, annotation.degree)} {annotationCategories(annotation.ana)}</span>
    <span> certainty: </span><AssertedValue annotation={annotation}/>.
    <span className={annotation?.desc?.length > 0 ? 'text-primary' : 'd-none'}>
      <br/><b>&quot;</b><i>{annotation.desc}</i><b>&quot;</b>
    </span>
  </React.Fragment>
}
