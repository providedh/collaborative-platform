import { useEffect } from 'react'

export default function useRender (width, height, data, timeline, containerRef) {
  useEffect(() => {
    timeline.render(data, containerRef.current)
    if (data !== null && data !== undefined && data.filtered?.count > 0) {
    }
  }, // Render
  [width, height, data, containerRef]) // Conditions*/
}
