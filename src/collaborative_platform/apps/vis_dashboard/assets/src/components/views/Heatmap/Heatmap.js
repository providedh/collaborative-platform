import React, { useEffect, useState, useRef } from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'
import css from './style.css' // eslint-disable-line no-unused-vars
import getConfig from './config'
import { DataClient, useCleanup } from '../../../data'
import useData from './data'
import render from './vis.js'

function handleEvent (dataClient, event) {
}

export default function Heatmap ({ layout, source, entityType }) {
  const [containerRef, vis, legendRef] = [useRef(), useRef(), useRef(), useRef()]
  const {width, height} = (containerRef.current !== undefined
    ? containerRef.current.getBoundingClientRect()
    : {width:0, height:0})

  const dataClient = useState(DataClient())[0]
  useCleanup(dataClient)
  const data = useData(dataClient, source, entityType)

  useEffect(() => render(data, vis.current, width, height),
    [data, vis.current, width, height])

  return (
    <div className={styles.heatmap} ref={containerRef}>
      <svg ref={vis} className={styles.heatmapSvg}>
        <g className="legend"></g>
      </svg>
    </div>
  )
}

Heatmap.prototype.description = 'Examine multivariate data, relationship among data, and evolution through time in ' +
    'a generalized manner user a color encoded grid array.'

Heatmap.prototype.getConfigOptions = getConfig

Heatmap.propTypes = {
  layout: PropTypes.shape({
    w: PropTypes.number,
    h: PropTypes.number
  }),
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node
  ]),
  tileLayout: PropTypes.string,
  colorScale: PropTypes.string,
  rangeScale: PropTypes.string,
  source: PropTypes.string,
  axis1: PropTypes.string,
  axis2: PropTypes.string
}
