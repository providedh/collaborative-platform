import * as d3 from 'd3' 

const heatmap = {
  cellPadding: .1,
  axisSpace: 70
}

function getBins(data) {
  const keys = Object.keys(data.all)
  const bins = []
  keys.forEach((y, j) => {
    keys.slice(0, j+1).forEach((x, i) => {
      bins.push({x, y, pos: [i, j]})
    })
  })
  return bins
}

function updateCell(cell, d, data, bandScale){
  const entries = [...data.all[d.x]].filter(x => data.all[d.y].has(x))

  cell
    .attr('transform', d => `translate(${bandScale(d.pos[0]) + heatmap.axisSpace}, ${bandScale(d.pos[1])})`)
  cell.select('rect')
    .attr('width', bandScale.bandwidth())
    .attr('height', bandScale.bandwidth())
    .attr('fill', 'skyblue')
  cell.select('text')
    .text(entries.length)
    .attr('x', bandScale.bandwidth()/2)
    .attr('y', bandScale.bandwidth()/2)
}

export default function render(data, svgNode, width, height) {
  if (data === null || width === 0 || height === 0) {return}
  const svg = d3.select(svgNode)
    .attr('width', width)
    .attr('height', height)

  const bins = getBins(data)
  const colorScale = d3.interpolateBlues
  const bandScale = d3.scaleBand()
    .domain(d3.range(Object.keys(data.all).length))
    .range([0, Math.min(width, height)-heatmap.axisSpace])
    .padding(heatmap.cellPadding)

  svg.selectAll('g.bin')
    .data(bins, d => `${d.x}-${d.y}`)
    .join(
      enter => enter
                .append('g')
                .classed('bin', true)
                .each(function(d){
                  const cell = d3.select(this)
                  cell.append('rect')
                    .attr('rx', 20)
                    .attr('ry', 20)
                  cell.append('text')
                  updateCell(d3.select(this), d, data, bandScale)
                }),
      update => update
                .each(function(d){
                  updateCell(d3.select(this), d, data, bandScale)
                })
      )

  const max = Math.max(...svg.selectAll('g.bin text').nodes().map(d => +d.textContent))
  svg.selectAll('g.bin').each(function(d) {
    const cell = d3.select(this)
    const count = +cell.select('text').text()
    cell.select('rect').attr('fill', colorScale(count / max))
  })
}