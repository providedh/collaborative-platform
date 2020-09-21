import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'
import css from './style.css' // eslint-disable-line no-unused-vars
import getConfig from './config'
import { useRender, MapRenderer } from './vis'
import { DataClient, useCleanup } from '../../../data'
import useData from './data'

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
export default function Map ({ layout, renderedItems, ...rest }) {
  const [mainMapRef, miniMapRef, miniMapOverlayRef, tableRef] = [useRef(), useRef(), useRef(), useRef()]
  const [width, height] = layout !== undefined ? [layout.w, layout.h] : [4, 4]
  const { context } = rest

  const dataClient = useState(DataClient())[0]
  useCleanup(dataClient)
  const data = useData(dataClient)
  const map = useState(MapRenderer())[0]
  useRender(
    map,
    width, 
    height, 
    data, 
    renderedItems, 
    context.taxonomy, 
    mainMapRef.current, 
    miniMapRef.current, 
    miniMapOverlayRef.current,
    tableRef.current,
    e => onEvent(e, dataClient, context))

  const places = data.entities.filtered
    .map(({id, properties, filename, file_id}) => 
      <tr key={id} onMouseEnter={() => onEvent({type: 'hover', target: file_id}, dataClient, context)}>
        <th className="text-nowrap" scope="row">{id}</th>
        <td>{properties.geo.split(' ')[0]}ª</td>
        <td>{properties.geo.split(' ')[1]}ª</td>
        <td className="text-break">{filename}</td>
      </tr>)

  return (
    <div className={styles.map + ' mapVis'}>
      <div className={styles.mainMap}>
        <canvas ref={mainMapRef}/>
      </div>
      <div className={styles.minimap + ' mapMinimap'}>
        <canvas ref={miniMapRef}/>
        <div ref={tableRef} className={styles.locationTable}>
          <table  className="table table-hover table-sm table-bordered">
            <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">Lat</th>
                <th scope="col">Long</th>
                <th scope="col">Document</th>
              </tr>
            </thead>
            <tbody>
              {places}
            </tbody>
          </table>
        </div>
      </div>
      <div className={styles.minimap + ' mapMinimap'}>
        <canvas ref={miniMapOverlayRef}/>
      </div>
      <span className={data.allNonValid > 0 ? '' : 'd-none'}>{data.allNonValid} place entities with <i>geo</i> property missing.</span>
    </div>
  )
}

Map.prototype.description = 'Place and explore place entities and annotations based on their'+
' geographical location.'

Map.prototype.getConfigOptions = getConfig

Map.propTypes = {
  layout: PropTypes.shape({
    w: PropTypes.number,
    h: PropTypes.number
  }),
  rest: PropTypes.object,
  renderedItems: PropTypes.string
}
