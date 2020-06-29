import React from 'react'
import { render } from 'react-dom'

import { TEIentities } from 'common/types'
import { App } from 'components/app'

const appConfig = {
  projectId: window.project_id,
  user: 'annotator-1',
  fileId: window.file_id,
  fileVersion: window.file_version,
  fileName: window.file_name,
  configuration: window.preferences
}

TEIentities.update(appConfig.configuration.properties_per_entity)

render(<App {...appConfig}/>, document.getElementById('react-root'))
