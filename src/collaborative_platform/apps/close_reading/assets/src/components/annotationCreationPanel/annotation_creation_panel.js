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
import styles from './annotation_creation_panel.module.css'
import AnnotateForm from './annotate_form.js'

export default function AnnotationCreationPanelWithContext (props) {
  return (
    <WithAppContext>
      <AnnotationCreationPanel {...props}/>
    </WithAppContext>
  )
}

function onTagCreate (selection, annotation, websocket) {
  const tagBuilder = AtomicActionBuilder(ActionTarget.text, ActionType.add, ActionObject.tag)
  const certBuilder = AtomicActionBuilder(ActionTarget.certainty, ActionType.add, ActionObject.certainty)
  const tagAction = tagBuilder(...selection.target)
  const certAction = certBuilder(
    0,
    annotation.locus,
    annotation.ana,
    annotation.cert,
    annotation.assertedValue,
    annotation.desc)

  const request = WebsocketRequest(WebsocketRequestType.modify, [tagAction, certAction])
  websocket.send(request)
}

function AnnotationCreationPanel (props) {
  const [annotation, setAnnotation] = useState(null)

  return <div className={styles.annotationCreationPanel}>
    <form>
      <div>
        <AnnotateForm onChange={annotation => setAnnotation(annotation)}/>
      </div>
      <div className="row mt-2 flex-column mx-1">
        <div className="d-flex flex-row justify-content-between">
          <span className={styles.step}>1</span>
          <span className={styles.step}>2</span>
        </div>
        <div className="progress my-1" style={{ height: '2px' }}>
          <div className="progress-bar" role="progressbar" style={{ width: '0%' }} aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
        </div>
        <div className="d-flex flex-row justify-content-between">
          <button type="button" className="btn btn-link dotted-link">Fill annotation details</button>
          <button className="btn btn-outline-primary btn-sm"
            onClick={e => {
              e.preventDefault()
              onTagCreate(props.selection, annotation, props.context.websocket)
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
