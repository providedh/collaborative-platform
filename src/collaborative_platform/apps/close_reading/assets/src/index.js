import React from 'react'
import { render } from 'react-dom'

import { App } from 'components/app'

const appConfig = {
  projectId: window.project_id,
  user: 'annotator-1',
  fileId: window.file_id,
  fileVersion: window.file_version,
  fileName: 'Historical file',
  configuration: window.preferences
}

render(<App {...appConfig}/>, document.getElementById('react-root'))
