import React from 'react'
import PropTypes from 'prop-types'

import { SelectionType } from 'common/types'
import styles from './tooltip.module.css'
import { EntityPanel } from 'components/entityPanel'
import { SelectionPanel } from 'components/selectionPanel'

export default function Tooltip (props) {
  const { selection } = props

  if (document.getElementById('document') == null) { return '' }
  if (selection === null) { return '' }
  const box = document.getElementById('document').getBoundingClientRect()

  const position = {
    top: (selection?.screenY - 20) + 'px'
  }

  const innerPadding = 10
  if (selection?.screenX - 120 < box.left) {
    position.left = (box.left + innerPadding) + 'px'
  } else if ((selection?.screenX - 120 + 400) > box.right) {
    position.right = `calc(100vw - ${(box.right - innerPadding)}px)`
  } else {
    position.left = (selection?.screenX - 120) + 'px'
  }

  const cssClasses = [
    'mt-4',
    styles.tooltip
  ]

  return <div className={cssClasses.join(' ')} style={position}>
    {selection.type === SelectionType.textSelection
      ? <SelectionPanel selection={selection}/>
      : <EntityPanel selection={selection}/>}
  </div>
}

Tooltip.propTypes = {
  selection: PropTypes.shape({
    type: PropTypes.string,
    target: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.arrayOf(PropTypes.number)
    ]),
    screenX: PropTypes.number,
    screenY: PropTypes.number
  })
}
