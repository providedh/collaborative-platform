import React from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'

import { WithAppContext } from 'app_context'
import VersionsTimeline from './VersionsTimeline'
import Form from '../../ui/Form'

export default function DataSelectionPanelWithContext (props) {
  return (
    <WithAppContext>
      <DataSelectionPanel {...props}/>
    </WithAppContext>
  )
}

function DataSelectionPanel ({ currentVersion, authors = [], context, setVersion, setAuthors }) {
  const collaboratorNames = context.contributors.map(x => `${x.first_name} ${x.last_name}`)
  const collaborators = context.contributors.map(x => x.id)
  const handleAuthorChange = conf => setAuthors(conf[0].value)

  return (
    <div className={styles.dataSelectionPanel}>
      <h5>Authorships</h5>
      <h6>Only consider work of</h6>
      <Form options={[{
        name: 'Only consider work from',
        type: 'compactMultipleSelection',
        value: authors,
        params: { options: collaborators, labels: collaboratorNames }
      }]}
      onUpdate={handleAuthorChange}/>
      <h5 className="mt-3">Data Versioning</h5>
      <h6>Use a specific version of the project</h6>
      <VersionsTimeline selected={currentVersion} onChange={setVersion} />
    </div>
  )
}

DataSelectionPanel.propTypes = {
  currentVersion: PropTypes.number,
  authors: PropTypes.array,
  context: PropTypes.shape({
    contributors: PropTypes.array
  }),
  setVersion: PropTypes.func,
  setAuthors: PropTypes.func
}
