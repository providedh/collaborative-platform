import { useEffect } from 'react'

import Map from './map'

export default function useRender (width, height, data, dimension, taxonomy, mainMapRef, miniMapRef, callback) {
  const map = Map()
  map.setTaxonomy(taxonomy)
  map.setEventCallback(callback)

  useEffect(() => {
    map.render(data, dimension, mainMapRef.current, miniMapRef.current)
    if (data !== null && data !== undefined && data.filtered?.count > 0) {
    }
  }, // Render
  [width, height, data, dimension, mainMapRef, miniMapRef]) // Conditions*/
}
