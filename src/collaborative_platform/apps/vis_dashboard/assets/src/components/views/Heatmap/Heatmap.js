import React, { useEffect, useState, useRef } from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'
import css from './style.css' // eslint-disable-line no-unused-vars
import getConfig from './config'
import { RegularHeatmapBuilder, StairHeatmapBuilder, HeartHeatmapBuilder, Director } from './vis'
import { DataClient, useCleanup } from '../../../data'
import useData from './data'

function useHeatmap (layout, colorScale, rangeScale, eventCallback) {
  const [heatmap, setHeatmap] = useState(null)
  useEffect(() => {
    let builder = RegularHeatmapBuilder()
    if (layout === 'Split') { builder = StairHeatmapBuilder() }
    if (layout === 'Tilted') { builder = HeartHeatmapBuilder() }

    const director = Director(builder)
    director.make(colorScale, rangeScale, eventCallback)
    setHeatmap(builder.getResult())
  }, [layout, colorScale, rangeScale])

  return heatmap
}

function useRender (width, height, heatmap, data, containerRef, canvasRef, overlayCanvasRef, legendRef) {
  useEffect(() => {
    if (heatmap != null) { heatmap.render(data, containerRef.current, canvasRef.current, overlayCanvasRef.current, legendRef.current) }
  }, // Render
  [width, height, heatmap, data, containerRef, canvasRef, overlayCanvasRef, legendRef]) // Conditions*/
}

function handleEvent (dataClient, event) {
}

export default function Heatmap ({ layout, tileLayout, colorScale, rangeScale, source, axis1, axis2 }) {
  const [containerRef, canvasRef, overlayCanvasRef, legendRef] = [useRef(), useRef(), useRef(), useRef()]
  const [width, height] = layout !== undefined ? [layout.w, layout.h] : [4, 4]

  const dataClient = useState(DataClient())[0]
  useCleanup(dataClient)
  const data = useData(dataClient, source, axis1, axis2)
  const heatmap = useHeatmap(tileLayout, colorScale, rangeScale, event => handleEvent(dataClient, event))

  useRender(width, height, heatmap, data, containerRef, canvasRef, overlayCanvasRef, legendRef)

  return (
    <div className={styles.heatmap} ref={containerRef}>
      <canvas ref={canvasRef} className={styles.canvas}/>
      <canvas className={styles.overlayCanvas} ref={overlayCanvasRef}/>
      <svg ref={legendRef} className={styles.legendBrush}/>
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
