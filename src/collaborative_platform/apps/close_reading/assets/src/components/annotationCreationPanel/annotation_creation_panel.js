import React, { useState } from 'react'
import PropTypes from 'prop-types'

import {
  ActionType,
  ActionTarget,
  ActionObject,
  AtomicActionBuilder,
  WebsocketRequest,
  WebsocketRequestType
} from 'common/types'
import { WithAppContext } from 'common/context/app'
import { EntitySelector } from 'components/entitySelector'
import styles from './annotation_creation_panel.module.css'
import AnnotateForm from './annotate_form.js'

export default function AnnotationCreationPanelWithContext (props) {
  return (
    <WithAppContext>
      <AnnotationCreationPanel {...props}/>
    </WithAppContext>
  )
}

function onTagCreate (selection, entityPayload, annotation, websocket) {
  const tagBuilder = AtomicActionBuilder(ActionTarget.text, ActionType.add, ActionObject.tag)
  const refBuilder = AtomicActionBuilder(ActionTarget.entity, ActionType.add, ActionObject.reference)
  const certBuilder = AtomicActionBuilder(ActionTarget.certainty, ActionType.add, ActionObject.certainty)
  const tagAction = tagBuilder(...selection.target)
  const refAction = refBuilder(0, entityPayload)
  const certAction = certBuilder(
    1,
    annotation.locus,
    annotation.ana,
    annotation.cert,
    annotation.assertedValue,
    annotation.desc)

  const request = WebsocketRequest(WebsocketRequestType.modify, [tagAction, refAction, certAction])
  websocket.send(request)
}

function AnnotationCreationPanel (props) {
  const [payload, setPayload] = useState(null)
  const [annotation, setAnnotation] = useState(null)
  const [step, setStep] = useState(0)

  let entityType = Object.keys(props.context.configuration.entities)[0]
  if (payload != null) {
    if (payload?.parameters?.entity_type !== undefined) {
      entityType = payload.parameters.entity_type
    } else if (payload?.new_element_id !== undefined) {
      const target = props.context.entities.filter(e => e.target.value === payload.new_element_id)?.[0]
      if (target !== undefined) {
        entityType = target.type
      }
    }
  }

  return <div className={styles.annotationCreationPanel}>
    <form>
      <div className={step === 0 ? '' : 'd-none'}>
        <EntitySelector onChange={newPayload => setPayload(newPayload)}/>
      </div>
      <div className={step === 1 ? '' : 'd-none'}>
        <AnnotateForm entity={entityType}
          onChange={annotation => setAnnotation(annotation)}/>
      </div>
      <div className="row mt-2 flex-column mx-1">
        <div className={styles.progressbar + ' position-relative'}>
          <div className="progress my-1 position-relative ">
            <div className="progress-bar" role="progressbar" style={{ width: (step * 50) + '%' }} aria-valuenow={50 + step * 50} aria-valuemin="0" aria-valuemax="100"></div>
          </div>
          <div className="d-flex flex-row justify-content-between position-relative">
            <span className={styles.step + ' ' + (step === 0 ? styles.current : '')}>1</span>
            <span className={styles.step + ' ' + (step === 1 ? styles.current : '')}>2</span>
            <span className={styles.step}>3</span>
          </div>
        </div>
        <div className="d-flex flex-row justify-content-between">
          <button type="button" onClick={() => setStep(0)} className="btn btn-link dotted-link">Specify entity</button>
          <button type="button" onClick={() => setStep(1)} className="btn btn-link dotted-link">Fill annotation details</button>
          <button className="btn btn-outline-primary btn-sm"
            onClick={e => {
              e.preventDefault()
              onTagCreate(props.selection, payload, annotation, props.context.websocket)
            }}
            type="button">Create</button>
        </div>
      </div>
    </form>
  </div>
}

AnnotationCreationPanel.propTypes = {
  callback: PropTypes.func,
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    entities: PropTypes.arrayOf(PropTypes.object),
    configuration: PropTypes.object,
    websocket: PropTypes.object
  }),
  selection: PropTypes.object
}
