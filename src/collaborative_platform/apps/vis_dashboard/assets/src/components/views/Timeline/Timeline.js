import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'
import css from './style.css' // eslint-disable-line no-unused-vars
import getConfig from './config'
import { useRender } from './vis'
import { DataClient, useCleanup } from '../../../data'
import useData from './data'

function onEvent (event, dataClient, context) {
  console.log(event, dataClient, context)
  /*
  if (event.action === 'click') {
    if (event?.target === 'unfilter') {
      dataClient.clearFilters()
    } else if (levels['level' + event.depth] === 'file') {
      dataClient.filter('fileId', x => x === (+event.data.name))
    } else if (levels['level' + event.depth] === 'file_name') {
      if (Object.hasOwnProperty.call(context.name2document, event.data.name)) { dataClient.filter('fileId', x => x === context.name2document[event.data.name].id) }
    } else {
      if (source === 'certainty') {
        const option2dimension = {
          category: 'certaintyCategory',
          degree: 'certaintyDegree',
          cert: 'certaintyCert',
          match: 'certaintyMatch',
          resp: 'certaintyAuthor'
        }
        const dimension = option2dimension[levels['level' + event.depth]]

        if (dimension === 'certaintyCategory') {
          dataClient.filter(dimension, x => x.includes(event.data.name))
        } else {
          dataClient.filter(dimension, x => x === event.data.name)
        }
      }
    }
  } else {
    if (levels['level' + event.depth] === 'file') {
      dataClient.focusDocument(event.data.name)
    } else if (levels['level' + event.depth] === 'file_name') {
      dataClient.focusDocument(context.name2document[event.data.name].id)
    }
  }
  */
}

// ...rest has both the levels and the injected context prop
export default function Timeline ({ layout, ...rest }) {
  const containerRef = useRef()
  const [width, height] = layout !== undefined ? [layout.w, layout.h] : [4, 4]
  const { context } = rest

  const dataClient = useState(DataClient())[0]
  useCleanup(dataClient)
  const data = useData(dataClient)
  
  console.log(data)
  useRender(width, height, data, context.taxonomy, containerRef, e => onEvent(e, dataClient, context))

  return (
    <div className={styles.timeline + ' Timeline'} ref={containerRef}>
      <svg>
        <g className="legend"></g>
        <g className="axis"></g>
      </svg>
      <svg className="entities">
      </svg>
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
