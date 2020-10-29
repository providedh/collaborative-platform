import * as d3 from 'd3' 

import styles from './style.module.css'

const heatmap = {
  cellPadding: .1,
  axisSpace: 70,
  axisWidth: 70
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
  const [left, top] = [
    bandScale(d.pos[0]),
    bandScale(d.pos[1]) + heatmap.axisSpace
  ]

  cell
    .attr('transform', d => `translate(${left}, ${top})`)
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

  heatmap.axisWidth = Math.max(...Object.keys(data.all).map(d => d.length)) * 8.3

  const bins = getBins(data)
  const colorScale = d3.interpolateBlues
  const bandScale = d3.scaleBand()
    .domain(d3.range(Object.keys(data.all).length))
    .range([0, Math.min(width - heatmap.axisWidth - heatmap.axisSpace, height - heatmap.axisSpace)])
    .padding(heatmap.cellPadding)

  svg.select('g.cells')
    .attr('transform', `translate(${heatmap.axisWidth + heatmap.axisSpace}, 0)`)
    .selectAll('g.bin')
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

  svg.select('g.legendX')
    .selectAll('text')
    .data(Object.keys(data.all), d => d)
    .join('text')
    .classed(styles.legend, true)
    .text(d => d)
    .attr('x', (d, i) => bandScale(i) +heatmap.axisSpace + heatmap.axisWidth + 10)
    .attr('y', (d, i) => heatmap.axisSpace + bandScale(i) - 10)

  svg.select('g.legendY')
    .selectAll('text')
    .data(Object.keys(data.all), d => d)
    .join('text')
    .classed(styles.legend, true)
    .text(d => d)
    .attr('x', heatmap.axisWidth + heatmap.axisSpace)
    .attr('y', (d, i) => heatmap.axisSpace + bandScale(i) + bandScale.bandwidth()/2)
    .style('text-anchor', 'end')
}