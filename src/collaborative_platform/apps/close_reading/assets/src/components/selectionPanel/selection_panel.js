import React, { useState } from 'react'
import PropTypes from 'prop-types'

import {
  WebsocketRequest,
  WebsocketRequestType,
  ActionType,
  ActionTarget,
  ActionObject,
  AtomicActionBuilder
} from 'common/types'
import { AnnotationCreationPanel } from 'components/annotationCreationPanel'
import { EntityCreationPanel } from 'components/entityCreationPanel'
import styles from './selection_panel.module.css'

import { WithAppContext } from 'common/context/app'

export default function CreateAttributeWithContext (props) {
  return (
    <WithAppContext>
      <SelectionPanel {...props}/>
    </WithAppContext>
  )
}

const CreationOption = { entity: 'Add entity', certainty: 'Annotate uncertainty' }

function Navigation (option, setOption) {
  const navigation = (option === null
    ? (<div className={styles.navigation}>
      <button type="button"
        className="btn btn-sm btn-primary"
        onClick={() => setOption(CreationOption.entity)}>
          Add entity
      </button>
      <button type="button"
        className="btn btn-sm btn-primary ml-3"
        onClick={() => setOption(CreationOption.certainty)}>
          Annotate uncertainty
      </button>
    </div>)
    : (<div className={styles.navigation}>
      <button type="button"
        className="btn btn-link btn-sm"
        onClick={() => setOption(null)}>
          &lt; Back
      </button>
      <button disabled type="button" className="btn btn-sm btn-light">{option}</button>
      <hr className="m-0"/>
    </div>)
  )
  return navigation
}

function onTagCreate (selection, entity, attributes, websocket) {
  const tagBuilder = AtomicActionBuilder(ActionTarget.text, ActionType.add, ActionObject.tag)
  const tagAction = tagBuilder(...selection.target)

  // const attributeBuilder = AtomicActionBuilder(ActionTarget.entity, ActionType.add, ActionObject.property)
  // const attributeAction = attributeBuilder('TEMP', attributes)
  // const actions = [tagAction, attributeAction]
  const request = WebsocketRequest(WebsocketRequestType.modify, [tagAction])
  console.log(request)
  websocket.send(request)
  // alert(JSON.stringify(actions))
}

function SelectionPanel (props) {
  const [option, setOption] = useState(null)

  let body = ''
  if (option !== null) {
    body = (option === CreationOption.certainty
      ? <AnnotationCreationPanel />
      : <EntityCreationPanel callback={(entity, attributes) =>
        onTagCreate(props.selection, entity, attributes, props.context.websocket)}/>)
  }

  const bodyCssClasses = ['card-body']
  if (body === '') { bodyCssClasses.push('d-none') }

  return <div className={styles.selectionPanel + ' card'}>
    <div className="card-header">
      {Navigation(option, setOption)}
    </div>
    <div className={bodyCssClasses.join(' ')}>
      {body}
    </div>
  </div>
}

SelectionPanel.propTypes = {
  selection: PropTypes.object,
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    entities: PropTypes.object,
    configuration: PropTypes.object,
    websocket: PropTypes.object
  })
}
