import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'
import css from './style.css' // eslint-disable-line no-unused-vars
import getConfig from './config'
import { useRender } from './vis'
import { DataClient, useCleanup } from '../../../data'
import useData from './data'
import TimelineVis from './vis/timeline'

function onEvent (event, dataClient, context) {
  if (event.type === 'zoom') {
    if (event.filtered === null) {
      dataClient.clearFilters()
    } else {
      dataClient.filter('entityId', d => event.filtered.includes(d))
    }
  } else if (event.type === 'hover') {
    dataClient.focusDocument(event.target)
  }
}

// ...rest has both the levels and the injected context prop
export default function Timeline (props) {
  const { layout, ...rest } = props
  const containerRef = useRef()
  const [width, height] = layout !== undefined ? [layout.w, layout.h] : [4, 4]
  const { context } = rest

  const dataClient = useState(DataClient())[0]
  useCleanup(dataClient)
  const data = useData(dataClient)
  const timeline = useState(TimelineVis())[0]
  timeline.setTaxonomy(rest.context.taxonomy)
  timeline.setEventCallback(e => onEvent(e, dataClient, rest.context))
  
  useRender(width, height, data, timeline, containerRef)

  return (
    <div className={styles.timeline + ' Timeline'} ref={containerRef}>
      <div className='header'>
        
      </div>
      <svg className="back">
        <g className="axis"></g>
      </svg>
      <div className={styles.entityContainer}>
        <svg className="entities"></svg>
      </div>
    </div>
  )
}

Timeline.prototype.description = 'Arrange time entities in a horizontal axis along ' + 
'with the level sources and the documents involved.'

Timeline.prototype.getConfigOptions = getConfig

Timeline.propTypes = {
  layout: PropTypes.shape({
    w: PropTypes.number,
    h: PropTypes.number
  }),
  rest: PropTypes.object,
  dimension: PropTypes.string
}
