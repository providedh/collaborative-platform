import { useEffect } from 'react'

import Map from './map'

export default function useRender (width, height, data, dimension, taxonomy, mainMapRef, miniMapRef, miniMapOverlayRef, tableRef, callback) {
  const map = Map()
  map.setTaxonomy(taxonomy)
  map.setEventCallback(callback)

  useEffect(() => {
    map.render(data, dimension, mainMapRef, miniMapRef, miniMapOverlayRef, tableRef)
    if (data !== null && data !== undefined && data.filtered?.count > 0) {
    }
  }, // Render
  [width, height, data, dimension, mainMapRef, miniMapRef, tableRef, miniMapOverlayRef]) // Conditions*/
}
