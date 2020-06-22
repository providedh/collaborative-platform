import React, { useState } from 'react'
import PropTypes from 'prop-types'

import {AnnotationCreationPanel} from 'components/annotationCreationPanel'
import {EntityCreationPanel} from 'components/entityCreationPanel'
import styles from './selection_panel.module.css'

const CreationOption = {entity: 'Add entity', certainty: 'Annotate uncertainty'}

function Navigation (option, setOption) {
  const navigation = (option === null
    ? (<div className={styles.navigation}>
        <button type="button" 
                className="btn btn-primary" 
                onClick={()=>setOption(CreationOption.entity)}>
          Add entity
        </button>
        <button type="button" 
                className="btn btn-primary ml-3"
                onClick={()=>setOption(CreationOption.certainty)}>
          Annotate uncertainty
        </button>
        </div>)
    : (<div className={styles.navigation}>
        <button type="button" 
                className="btn btn-link"
                onClick={()=>setOption(null)}>
          &lt; Back
        </button>
        <button disabled type="button" className="btn btn-light">{option}</button>
        <hr className="m-0"/>
        </div>)
  )
  return navigation
}

export default function SelectionPanel (props) {
  const [option, setOption] = useState(null)

  let body = '';
  if (option !== null) {
    body = (option === CreationOption.certainty
      ? <AnnotationCreationPanel />
      : <EntityCreationPanel />)
  }

  let bodyCssClasses = ['card-body']
  if (body === '') {bodyCssClasses.push('d-none')}

  return <div className={styles.selectionPanel + ' card'}>
    <div className="card-header">
      {Navigation(option, setOption )}
    </div>
    <div className={bodyCssClasses.join(' ')}>
      {body}
    </div>
  </div>
}