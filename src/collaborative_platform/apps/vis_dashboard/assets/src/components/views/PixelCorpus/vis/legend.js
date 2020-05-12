import * as _d3 from 'd3'
import d3Legend from 'd3-svg-legend'
const d3 = Object.assign(_d3, d3Legend)

export default function renderLegend (svg, legendWidth, padding, colorScale, source) {
  const { width } = svg.getBoundingClientRect()

  const legend = d3.legendColor()
    .title(source[0].toUpperCase() + source.slice(1))
    .shape('path', d3.symbol().type(d3.symbolSquare).size(150)())
    .shapePadding(0)
    .scale(colorScale)

  d3.select(svg)
    .select('.legend')
    .call(legend)
    .transition()
    .attr('transform', `translate(${width - legendWidth - padding}, ${padding * 3})`)
}
