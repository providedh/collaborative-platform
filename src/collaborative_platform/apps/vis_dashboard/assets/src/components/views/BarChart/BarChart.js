import React, { useEffect, useState, useRef } from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'
import css from './style.css' // eslint-disable-line no-unused-vars
import render from './render'
import getConfig from './config'
import useData from './data'
import { DataClient, useCleanup } from '../../../data'
import getOnEventCallback from './event'

export default function BarChart ({ layout, dimension, barDirection, entityType=null, context}) {
  const [refContainer, refCanvas, refOverlayCanvas] = [useRef(), useRef(), useRef()]
  const [width, height] = layout !== undefined ? [layout.w, layout.h] : [4, 4]

  const dataClient = useState(DataClient())[0]
  useCleanup(dataClient)
  const data = useData(dataClient, dimension, entityType)
  const onEvent = getOnEventCallback(dataClient, data?.filterDimension, data?.all)

  useEffect(() => render(
    refContainer.current,
    refCanvas.current,
    refOverlayCanvas.current,
    data,
    barDirection,
    onEvent), // Render
  [width, height, barDirection, data]) // Conditions

  return (
    <div className={styles.histogram} ref={refContainer}>
      <canvas ref={refCanvas}/>
      <canvas className={styles.overlayCanvas} ref={refOverlayCanvas}/>
    </div>
  )
}

BarChart.prototype.getConfigOptions = getConfig
BarChart.prototype.description = 'Encode frequencies using horizontal or vertical bars.'

BarChart.propTypes = {
  layout: PropTypes.shape({
    w: PropTypes.number,
    h: PropTypes.number
  }),
  dimension: PropTypes.string,
  barDirection: PropTypes.string
}
