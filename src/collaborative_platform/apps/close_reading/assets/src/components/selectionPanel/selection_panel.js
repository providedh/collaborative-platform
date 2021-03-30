import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { AnnotationCreationPanel } from 'components/annotationCreationPanel'
import { EntityAndUncertaintyCreationPanel } from 'components/entityAndUncertaintyCreationPanel'
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

const CreationOption = { entity: 'Add entity', uncertainty: 'Annotate uncertainty', both: 'Annotate entity and uncertainty' }

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
        onClick={() => setOption(CreationOption.uncertainty)}>
          Annotate uncertainty
      </button>
      <button type="button"
        className="btn btn-sm btn-primary ml-3"
        onClick={() => setOption(CreationOption.both)}>
          Annotate entity and uncertainty
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

function SelectionPanel (props) {
  const [option, setOption] = useState(null)

  let body = ''
  if (option !== null) {
    switch(option) {
      case CreationOption.entity:
        body = <EntityCreationPanel selection={props.selection}/>
        break
      case CreationOption.uncertainty:
        body = <AnnotationCreationPanel selection={props.selection}/>
        break
      case CreationOption.both:
        body = <EntityAndUncertaintyCreationPanel selection={props.selection}/>
        break
    }
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
    entities: PropTypes.arrayOf(PropTypes.object),
    configuration: PropTypes.object,
    websocket: PropTypes.object
  })
}
