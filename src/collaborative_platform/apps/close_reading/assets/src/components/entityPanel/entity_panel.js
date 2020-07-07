import React from 'react'
import PropTypes from 'prop-types'

import { ActionType, ActionTarget, ActionObject, AtomicActionBuilder } from 'common/types'
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

function onDeleteClick (id) {
  const builder = AtomicActionBuilder(ActionTarget.text, ActionType.delete, ActionObject.tag)
  const action = builder(id)
  alert(JSON.stringify(action))
}

function EntityPanel (props) {
  const style = props.context.configuration.entities[props.selection.target.type]
  const icon = style.icon

  return <div className={styles.entityPanel}>
    <div className="card">
      <div className="card-header d-flex justify-content-between">
        <div>
          <span className={styles.icon} style={{ color: style.color }} dataicon={icon}>
            <div dangerouslySetInnerHTML={{ __html: icon }} />
          </span>
          <h5 className="d-inline">
            {props.selection?.target?.type}
            <span className={styles.entityType}> ({props.selection.target.type})</span>
          </h5>
        </div>
        <span className={props.selection.target.saved === false ? 'ml-4 text-danger' : 'd-none'}>
          (unsaved)
          <button type="button"
            onClick={() => onDeleteClick(props.selection.target.id)}
            className="btn btn-link p-0 mx-1 text-danger">
            <u> -delete</u>
          </button>
        </span>
      </div>
      <div className="card-body">

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
    entities: PropTypes.object,
    configuration: PropTypes.object
  })
}
