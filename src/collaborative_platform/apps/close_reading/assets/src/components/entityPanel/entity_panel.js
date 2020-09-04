import React from 'react'
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
import styles from './entity_panel.module.css'
import Annotations from './annotations.js'
import Attributes from './attributes.js'

export default function EntityPanelWithContext (props) {
  return (
    <WithAppContext>
      <EntityPanel {...props}/>
    </WithAppContext>
  )
}

function onDeleteClick (id, websocket) {
  const deleteAction = AtomicActionBuilder(ActionTarget.text, ActionType.delete, ActionObject.tag)(id)

  const request = WebsocketRequest(WebsocketRequestType.modify, [deleteAction])
  websocket.send(request)
}

function onDiscardClick (id, websocket) {
  const request = WebsocketRequest(WebsocketRequestType.discard, [id])
  websocket.send(request)
}

function onRestoreClick (id, websocket) {
  const request = WebsocketRequest(WebsocketRequestType.discard, [id])

  websocket.send(request)
}

function EntityPanel (props) {
  const style = props.context.configuration.entities[props.selection.target.type]
  const icon = style.icon
  const deleted = props.selection.target.deleted === true
  const saved = !deleted && props.selection.target.saved === true

  return <div className={styles.entityPanel}>
    <div className="card">
      <div className="card-header d-flex justify-content-between">
        <div className={deleted === false ? '' : 'text-danger'}>
          <span className={styles.icon + (deleted === false ? '' : ' text-danger')} style={{ color: style.color }} dataicon={icon}>
            <div dangerouslySetInnerHTML={{ __html: icon }} />
          </span>
          <h5 className="d-inline">
            {props.selection?.target?.target?.value}
            <span className={styles.entityType + (deleted === false ? '' : 'text-danger')}> ({props.selection.target.type})</span>
          </h5>
        </div>
        <span className={deleted === true ? 'ml-4 text-danger' : 'd-none'}>
          (deleted)
          <button type="button"
            onClick={e => {
              e.preventDefault()
              const operation = props.context.operations.filter(x => (
                x.edited_element_id === props.selection.target.id.value &&
                x.element_type === 'tag' &&
                x.method === 'DELETE'
              ))

              if (operation.length !== 1) { return }

              onRestoreClick(operation[0].id, props.context.websocket)
            }}
            className="btn btn-link p-0 mx-1 text-primary">
            <u> restore</u>
          </button>
        </span>
        <span className={props.selection.target.saved === false ? 'ml-4 text-danger' : 'd-none'}>
          (unsaved)
          <button type="button"
            onClick={e => {
              e.preventDefault()
              const operation = props.context.operations.filter(x => (
                x.operation_result === props.selection.target.id.value &&
                x.element_type === 'tag' &&
                x.method === 'POST'
              ))

              if (operation.length !== 1) { return }

              onDiscardClick(operation[0].id, props.context.websocket)
            }}
            className="btn btn-link p-0 mx-1 text-danger">
            <u> -discard</u>
          </button>
        </span>
        <span className={saved === true ? 'ml-4 text-danger' : 'd-none'}>
          <button type="button"
            onClick={() => onDeleteClick(props.selection.target.id.value, props.context.websocket)}
            className="btn btn-link p-0 mx-1 text-danger">
            <u> -delete</u>
          </button>
        </span>
      </div>
      <div className="card-body">
        <Attributes entity={props.selection.target}/>
        <Annotations entity={props.selection.target}/>
      </div>
    </div>
  </div>
}

EntityPanel.propTypes = {
  selection: PropTypes.shape({
    type: PropTypes.string,
    target: PropTypes.oneOfType([
      PropTypes.object,
      PropTypes.arrayOf(PropTypes.number)
    ]),
    screenX: PropTypes.number,
    screenY: PropTypes.number
  }),
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    configuration: PropTypes.object,
    operations: PropTypes.arrayOf(PropTypes.object),
    websocket: PropTypes.object
  })
}
