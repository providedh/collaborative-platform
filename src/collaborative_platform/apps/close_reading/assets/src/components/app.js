import React, { useState } from 'react'
import PropTypes from 'prop-types'

import css from 'common/style/theme.css' // eslint-disable-line no-unused-vars
import { SelectionContext } from 'common/context/selection_context'
import Document from './document'

export default function App (props) {
  const [selection, setSelection] = useState(null)
  return (
    <SelectionContext.Provider value={{ selection, setSelection }}>
      <h1>Close reading</h1>
      <Document />
    </SelectionContext.Provider>
  )
}

App.propTypes = {}
