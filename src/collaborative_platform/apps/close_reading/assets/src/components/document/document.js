import React, { useState, useRef, useEffect } from 'react'
import PropTypes from 'prop-types'

import { Selection, SelectionType } from 'common/types'
import { processSelection, getSelection } from 'common/helpers/text_selection'
import { WithAppContext } from 'common/context/app'
import styles from './document.module.css'
import useContentRendering from './content'
import Toolbar from './toolbar.js'

export default function DocumentWithContext (props) {
  return (
    <WithAppContext>
      <Document {...props}/>
    </WithAppContext>
  )
}

function handleSelection (container, selectionEvent, onSelection, onClickOut) {
  const processed = processSelection(selectionEvent)
  const domSelection = processed[0]

  if (domSelection == null) {
    onClickOut()
    return
  }

  const selection = Selection(
    SelectionType.textSelection,
    getSelection(container, domSelection),
    selectionEvent.clientX,
    selectionEvent.clientY)

  event.stopPropagation()
  onSelection(selection)
}

function useRenderingOptions () {
  const [renderEntities, setRenderEntities] = useState(true)
  const [colorEntities, setColorEntities] = useState(true)
  const [renderCertainty, setRenderCertainty] = useState(true)
  const [colorCertainty, setColorCertainty] = useState(true)

  return {
    renderEntities: { value: renderEntities, set: setRenderEntities },
    colorEntities: { value: colorEntities, set: setColorEntities },
    renderCertainty: { value: renderCertainty, set: setRenderCertainty },
    colorCertainty: { value: colorCertainty, set: setColorCertainty }
  }
}

function Document (props) {
  const ref = useRef()
  const {
    renderEntities,
    colorEntities,
    renderCertainty,
    colorCertainty
  } = useRenderingOptions()

  const callbacks = {
    onHover: props.onHover,
    onHoverOut: props.onHoverOut,
    onClick: props.onClick,
    onClickOut: props.onClickOut
  }

  useEffect(() => {
    useContentRendering(ref.current, props.documentContent, callbacks, props.context)
  }, [props.documentContent])

  const cssClasses = [
    styles.document,
    'border',
    'border-primary',
    'shadow-sm',
    'p-2',
    'm-2',
    'rounded'
  ]

  if (renderEntities.value === true) cssClasses.push('renderEntity')
  if (colorEntities.value === true) cssClasses.push('colorEntity')
  if (renderCertainty.value === true) cssClasses.push('renderCertainty')
  if (colorCertainty.value === true) cssClasses.push('colorCertainty')

  return <React.Fragment>
    <Toolbar
      renderEntities={renderEntities}
      colorEntities={colorEntities}
      renderCertainty={renderCertainty}
      colorCertainty={colorCertainty}/>
    <div
      id="document"
      ref={ref}
      onMouseUp = {e => handleSelection(ref.current, e, props.documentContent, props.onSelection, props.onClickOut)}
      className={cssClasses.join(' ')}></div>
  </React.Fragment>
}

Document.propTypes = {
  renderEntities: PropTypes.shape({
    value: PropTypes.bool,
    set: PropTypes.func
  }),
  colorEntities: PropTypes.shape({
    value: PropTypes.bool,
    set: PropTypes.func
  }),
  renderCertainty: PropTypes.shape({
    value: PropTypes.bool,
    set: PropTypes.func
  }),
  colorCertainty: PropTypes.shape({
    value: PropTypes.bool,
    set: PropTypes.func
  }),
  onHover: PropTypes.func,
  onHoverOut: PropTypes.func,
  onClick: PropTypes.func,
  onClickOut: PropTypes.func,
  onSelection: PropTypes.func,
  documentContent: PropTypes.string,
  content: PropTypes.shape({
  }),
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    entities: PropTypes.object,
    configuration: PropTypes.object
  })
}
