import { useEffect } from 'react'

import Timeline from './timeline'

export default function useRender (width, height, data, taxonomy, containerRef, callback) {
  const timeline = Timeline()
  timeline.setTaxonomy(taxonomy)
  timeline.setEventCallback(callback)

  useEffect(() => {
    timeline.render(data, containerRef.current)
    if (data !== null && data !== undefined && data.filtered?.count > 0) {
    }
  }, // Render
  [width, height, data, containerRef]) // Conditions*/
}
