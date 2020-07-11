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
      <div className="row mt-2">
        <div className="form-group col-4">
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
