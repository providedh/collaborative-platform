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
import styles from './entity_creation_panel.module.css'

export default function EntityCreationPanelWithContext (props) {
  return (
    <WithAppContext>
      <EntityCreationPanel {...props}/>
    </WithAppContext>
  )
}

function onTagCreate (selection, entityPayload, websocket) {
  const tagBuilder = AtomicActionBuilder(ActionTarget.text, ActionType.add, ActionObject.tag)
  const refBuilder = AtomicActionBuilder(ActionTarget.entity, ActionType.add, ActionObject.reference)
  const tagAction = tagBuilder(...selection.target)
  const refAction = refBuilder(0, entityPayload)

  const request = WebsocketRequest(WebsocketRequestType.modify, [tagAction, refAction])
  websocket.send(request)
}

function EntityCreationPanel (props) {
  const [payload, setPayload] = useState(null)

  return <div className={styles.entityCreationPanel}>
    <form>
      <EntitySelector onChange={newPayload => setPayload(newPayload)}/>
      <div className="row mt-2 flex-column mx-1">
        <div className="d-flex flex-row justify-content-between">
          <span className={styles.step}>1</span>
          <span className={styles.step}>2</span>
        </div>
        <div className="progress my-1" style={{ height: '2px' }}>
          <div className="progress-bar" role="progressbar" style={{ width: '0%' }} aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
        </div>
        <div className="d-flex flex-row justify-content-between">
          <button type="button" className="btn btn-link dotted-link">Fill entity details</button>
          <button className="btn btn-outline-primary btn-sm"
            onClick={e => {
              e.preventDefault()
              onTagCreate(props.selection, payload, props.context.websocket)
            }}
            type="button">Create</button>
        </div>
      </div>
    </form>
  </div>
}

EntityCreationPanel.propTypes = {
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
