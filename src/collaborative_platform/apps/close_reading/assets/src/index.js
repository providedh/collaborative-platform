import React from "react";
import { render } from "react-dom";

import { App } from 'components/app'
import defaultTaxonomy from './default_taxonomy.js'

const app_config = {
  projectId: '12',
  user: 'annotator-1',
  fileId: '11',
  fileVersion: '12',
  fileName: 'Historical file',
  configuration: defaultTaxonomy
}

render(<App {...app_config}/>, document.getElementById('react-root'))
