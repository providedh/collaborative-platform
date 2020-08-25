import { useEffect } from 'react'

import Sunburst from './sunburst'

export default function useRender (width, height, data, dimension, taxonomy, containerRef, callback) {
  //const sunburst = Sunburst()

  useEffect(() => {
    if (data !== null && data !== undefined && data.filtered?.count > 0) {
      //sunburst.setTaxonomy(taxonomy)
      //sunburst.setEventCallback(callback)
      //sunburst.render(data, source, levels, containerRef.current)
    }
  }, // Render
  [width, height, data, dimension, containerRef]) // Conditions*/
}
