import * as d3 from 'd3' 

import styles from './style.module.css'

const heatmap = {
  cellPadding: .1,
  axisSpace: 35,
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
  const xEntries = data.filtered[d.x]
  const yEntries = data.filtered[d.y]
  const filteredOut = xEntries === undefined || yEntries === undefined
  const entries = filteredOut ? -1 : [...xEntries].filter(x => yEntries.has(x)).length
  
  const [left, top] = [
    bandScale(d.pos[0]),
    bandScale(d.pos[1]) + heatmap.axisSpace
  ]

  cell
    .attr('transform', d => `translate(${left}, ${top})`)
  cell.select('rect')
    .attr('width', bandScale.bandwidth())
    .attr('height', bandScale.bandwidth())

  cell.select('text')
    .text(entries)
    .attr('x', bandScale.bandwidth()/2)
    .attr('y', bandScale.bandwidth()/2)
}

function updateFIltered(cell, d, data, bandScale){
  const [left, top] = [
    bandScale(d.pos[0]),
    bandScale(d.pos[1]) + heatmap.axisSpace
  ]

  cell
    .attr('transform', d => `translate(${left}, ${top})`)
  cell.select('rect')
    .attr('width', bandScale.bandwidth())
    .attr('height', bandScale.bandwidth())
    .attr('fill', 'lightgrey')
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
    .range([0, Math.min(width - heatmap.axisWidth - heatmap.axisSpace, height - heatmap.axisSpace - 10)])
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

  svg.select('g.filtered')
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
                  updateFIltered(d3.select(this), d, data, bandScale)
                }),
      update => update
                .each(function(d){
                  updateFIltered(d3.select(this), d, data, bandScale)
                })
      )

  const max = Math.max(...svg.selectAll('g.cells g.bin text').nodes().map(d => +d.textContent))
  svg.selectAll('g.cells g.bin').each(function(d) {
      const cell = d3.select(this)
      const count = +cell.select('text').text()
      cell.classed(styles.filteredOut, count === -1)
      cell.select('rect').attr('fill', colorScale(count / max))
      cell.on('mouseenter', function(event, d){
        d3.select(event.target).classed(styles.focused, true)
        svg.select(`.x-${d.x.replace(' ', '-')}`).classed(styles.focused, true)
        svg.select(`.y-${d.y.replace(' ', '-')}`).classed(styles.focused, true)
      })
      cell.on('mouseleave', function(event, d){
        d3.selectAll('.'+styles.focused).classed(styles.focused, false)
      })
    })

  svg.select('g.legendX')
    .selectAll('text')
    .data(Object.keys(data.all), d => d)
    .join('text')
    .classed(styles.legend, true)
    .each(function(d){d3.select(this).classed('x-'+d.replace(' ', '-'), true)})
    .text(d => d)
    .attr('x', (d, i) => bandScale(i) +heatmap.axisSpace + heatmap.axisWidth + 10)
    .attr('y', (d, i) => heatmap.axisSpace + bandScale(i) - 10)

  svg.select('g.legendY')
    .selectAll('text')
    .data(Object.keys(data.all), d => d)
    .join('text')
    .classed(styles.legend, true)
    .each(function(d){d3.select(this).classed('y-'+d.replace(' ', '-'), true)})
    .text(d => d)
    .attr('x', heatmap.axisWidth + heatmap.axisSpace)
    .attr('y', (d, i) => heatmap.axisSpace + bandScale(i) + bandScale.bandwidth()/2)
    .style('text-anchor', 'end')
}