import { useEffect } from 'react'

import Sunburst from './sunburst'

export default function useRender (width, height, data, source, levels, taxonomy, containerRef, callback) {
  const levelKeys = Object.entries(levels).sort((x, y) => x[0] - y[0]).map(x => x[1])
  const sunburst = Sunburst()

  useEffect(() => {
    if (data !== null && data !== undefined && data.filtered?.count > 0) {
      sunburst.setTaxonomy(taxonomy)
      sunburst.setEventCallback(callback)
      sunburst.render(data, source, levels, containerRef.current)
    }
  }, // Render
  [width, height, data, levelKeys.join('_'), containerRef]) // Conditions*/
}
