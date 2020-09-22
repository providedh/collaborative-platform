import React from 'react'
import { render } from 'react-dom'

import { App } from 'components/app'

const appConfig = {
  projectId: window.project_id,
  projectName: window.project_name,
  user: window.user_id,
  configuration: window.preferences
}

render(<App {...appConfig}/>, document.getElementById('react-root'))
