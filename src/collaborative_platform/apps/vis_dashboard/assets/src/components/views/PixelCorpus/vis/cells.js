import * as d3 from 'd3'
import styles from '../style.module.css'
import PixelCorpusSource from '../config'

export default function renderCells (args) {
  const {
    svg,
    docOrder,
    fileAccessor,
    data,
    freeSpace,
    source,
    _entityColorScale,
    _colorBy,
    _eventCallback,
    _padding,
    _titleHeight,
    _maxRowItems,
    _docNameWidth,
    _maxLabelLength,
    _minSideLength
  } = args

  const title = (source === PixelCorpusSource.entities ? 'Entities' : 'Annotations') + ' in the corpus'
  const cellsByDoc = getCellsPerDoc(data, fileAccessor)
  const [rowsByDoc, maxItems] = getRowsByDoc(cellsByDoc, _maxRowItems, _minSideLength)

  const { height } = svg.getBoundingClientRect()
  const rootG = d3.select(svg)
    .select('g.vis')
    .attr('transform', `translate(${_padding}, ${_padding})`)
  const cellPadding = 3
  const cellSide = getCellSide(maxItems, rowsByDoc, freeSpace, height - (_padding * 2 + _titleHeight), cellPadding, _maxRowItems)

  // render title
  rootG.select('.title')
    .attr('x', 0)
    .attr('y', 22)// font size
    .text(title)

  renderDocumentLabels(docOrder, rowsByDoc, rootG, cellSide, _maxLabelLength, cellPadding, _titleHeight, _eventCallback)

  renderEntityCells(docOrder, cellsByDoc, rowsByDoc, rootG, cellSide, cellPadding, _titleHeight, _docNameWidth, _maxRowItems, _entityColorScale, _eventCallback, _colorBy)

  setupInteractions()
}

function priorRows (doc, rowsByDoc, docOrder) {
  const docIndex = docOrder[doc]
  const rowCount = Object.entries(docOrder)
    .reduce((ac, [name, idx]) => ac + (idx < docIndex ? rowsByDoc[name] : 0), 0)
  return rowCount
}

function shorttenedLabel (label, maxLabelLength = 20) {
  if (label.length <= maxLabelLength) { return label }

  const fragmentLength = Math.trunc(maxLabelLength / 2 - 2)
  const startFragment = label.slice(0, fragmentLength)
  const endFragment = label.slice(label.length - fragmentLength, label.length)
  return startFragment + '...' + endFragment
}

function renderDocumentLabels (docOrder, rowsByDoc, rootG, cellSide, maxLabelWidth, cellPadding, titleHeight, eventCallback) {
  const labels = rootG.select('.docLabels')
    .attr('transform', `translate(0, ${titleHeight - 11})`)
    .selectAll('text.' + styles.label)
    .data(Object.keys(docOrder))
  labels.exit().remove()
  labels.enter().append('svg:text').classed(styles.label, true)

  rootG.select('.docLabels').selectAll('text.' + styles.label)
    .text(d => shorttenedLabel(d, maxLabelWidth))
    .on('mouseenter', d => eventCallback('labelHover', d))
    .attr('x', 0)
    .transition()
    .duration(750)
    .ease(d3.easeLinear)
    .attr('y', d => priorRows(d, rowsByDoc, docOrder) * (cellSide + cellPadding))
}

function renderEntityCells (docOrder, data, rowsByDoc, rootG, cellSide, cellPadding, titleHeight, docNameWidth, maxRowItems, colorScale, eventCallback, colorBy) {
  const labels = rootG.select('.entityCells')
    .attr('transform', `translate(${docNameWidth + 10}, ${titleHeight - 22})`)
    .selectAll('g.doc')
    .data(Object.keys(docOrder))
  labels.exit().remove()
  labels.enter().append('svg:g').classed('doc', true)
  rootG.select('.entityCells').selectAll('g.doc')
    .each(function (d) {
      // console.log(data, d)
      const rects = d3.select(this)
        .selectAll('rect')
        .data(data[d].map((x, i) => Object.assign(x, { i })))
      rects.exit().remove()
      rects.enter().append('svg:rect')
    })
    .transition()
    .duration(750)
    .ease(d3.easeLinear)
    .attr('transform', d => `translate(0, ${priorRows(d, rowsByDoc, docOrder) * (cellSide + cellPadding)})`)

  rootG.select('.entityCells').selectAll('rect')
    .attr('width', cellSide)
    .attr('height', cellSide)
    .attr('x', d => (cellSide + cellPadding) * (d.i % maxRowItems))
    .attr('y', d => (cellSide + cellPadding) * Math.trunc(d.i / maxRowItems))
    .attr('stroke', 'black')
    .attr('fill', d => colorScale(d[colorBy]))
}

function setupInteractions () {

}

function getCellsPerDoc (data, accessor) {
  const cellsByDoc = {}
  data.all.forEach(e => {
    if (!Object.hasOwnProperty.call(cellsByDoc, accessor(e))) { cellsByDoc[accessor(e)] = [] }
    cellsByDoc[accessor(e)].push(e)
  })
  return cellsByDoc
}

function getRowsByDoc (cellsByDoc, maxRowItems, minSideLength) {
  let maxItems = 0
  const rowsByDoc = Object.fromEntries( // for entries [doc, lineCount]
    Object.entries(cellsByDoc)
      .map(([doc, entities]) => {
        if (maxItems < entities.length) {
          maxItems = entities.length
        }

        return [doc, 1 + (entities.length <= maxRowItems ? 0 : Math.trunc(entities.length / maxRowItems))]
      }))

  return [rowsByDoc, maxItems]
}

function getCellSide (maxItems, rowsByDoc, freeSpace, columnHeight, cellPadding, maxRowItems) {
  const rows = Object.values(rowsByDoc).reduce((ac, dc) => ac + dc, 0)
  const numItems = Math.min(maxItems, maxRowItems)
  const sideFittedByHeight = (columnHeight - (rows - 1) * cellPadding) / rows
  const sideFittedByWidth = (freeSpace - (numItems - 1) * cellPadding) / numItems
  const sideLength = Math.min(sideFittedByHeight, sideFittedByWidth)
  return sideLength
}
