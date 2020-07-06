import React, { useState } from 'react'
import { PropTypes } from 'prop-types'

import { WebsocketRequest, WebsocketRequestType} from 'common/types'
import { WithAppContext } from 'common/context/app'
import styles from './button.module.css'

export default function ButtonWithContext (props) {
  return (
    <WithAppContext>
      <Button {...props}/>
    </WithAppContext>
  )
}

function getSaveCallback(websocket, operations) {
  return () => {
    const request = WebsocketRequest(WebsocketRequestType.save, operations.map(o => o.id))
    console.log(request)
    websocket.send(request)
  }
}

function getDiscardCallback(websocket, operations) {
  return () => {
    const request = WebsocketRequest(WebsocketRequestType.discard, operations.map(o => o.id))
    console.log(request)
    websocket.send(request)
  }
}

function Button (props) {
  const [unfoiled, toggle] = useState(false)

  const operations = props.context.operations.map(o =>
    <li key={o.id} className="border-top py-1 list-group-item">
      {o.element_type} {o.method} {o.operation_result}
    </li>)

  const operationsStyles = [
    styles.operations,
    'list-group',
    'shadow-sm',
    (unfoiled === false ? 'd-none' : '')
  ].join(' ')

  return (
    <div className={styles.saveButton + ' align-items-end d-flex flex-column position-relative'}>
      <button 
          type="button" 
          className='btn btn-outline-primary' 
          onClick={getSaveCallback(props.context.websocket, props.context.operations)}>
        Save <span className="d-inline badge badge-primary badge-pill">{props.context.operations.length}</span>
      </button>
      <span className="text-primary" onClick={() => toggle(!unfoiled)}>
        {unfoiled === false
          ? <React.Fragment>see changes <i className=' fas fa-chevron-right'></i></React.Fragment>
          : <React.Fragment>hide changes <i className=' fas fa-chevron-down'></i></React.Fragment>
        }
      </span>
      <ul className={operationsStyles}>
        {operations}
        <button
          type="button"
          onClick={getDiscardCallback(props.context.websocket, props.context.operations)}
          className="py-1 border-top list-group-item-danger list-group-item list-group-item-action">
          Discard changes
        </button>
      </ul>
    </div>
  )
}

Button.propTypes = {
  context: PropTypes.shape({
    operations: PropTypes.arrayOf(PropTypes.object)
  })
}
