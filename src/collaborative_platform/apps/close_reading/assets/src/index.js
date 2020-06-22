import React from "react";
import { render } from "react-dom";

import { App } from 'components/app'
import defaultTaxonomy from './default_taxonomy.js'

const app_config = {
  projectId: window.project_id,
  user: 'annotator-1',
  fileId: window.file_id,
  fileVersion: window.file_version,
  fileName: 'Historical file',
  configuration: window.preferences
}

render(<App {...app_config}/>, document.getElementById('react-root'))
