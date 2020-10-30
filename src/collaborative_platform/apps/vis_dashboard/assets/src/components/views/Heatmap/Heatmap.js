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

  useEffect(() => {setTimeout(() => render(data, vis.current, width, height), 200)},
    [data, vis.current, width, height])

  const heatmapCssClasses = [
    styles.heatmapSvg,
    Object.keys(data.all).length === 0 ? styles.filteredOut : ''
  ].join(' ')

  return (
    <div className={styles.heatmap} ref={containerRef}>
      {Object.keys(data.all).length === 0
        ? <i>This view has no data to show either because the project does not have
            or current filters restrict all.</i>
        :''}
      <svg ref={vis} className={heatmapCssClasses}>
        <g className="filtered"></g>
        <g className="cells"></g>
        <g className="legendX"></g>
        <g className="legendY"></g>
      </svg>
    </div>
  )
}

Heatmap.prototype.description =
  'See how many entities have a property combination, concur in files, or how the taxonomy is used in annotations.'

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
