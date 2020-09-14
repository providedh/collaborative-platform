import * as d3_ from 'd3'
import * as d3Legend from 'd3-svg-legend'
const d3 = Object.assign({}, d3_, d3Legend)

import {dimOptions} from '../config'

/* Class: Timeline
 *
 *
 * */
export default function Timeline () {
  const self = {
    _eventCallback: null,
    _padding: 10,
    _legendHeight: 120,
    _timelineAxisHeight: 120
    //_extraVspacing: 50,
  }

  function _init () {
    self.setEventCallback = _getParameterSetter('_eventCallback')
    self.setTaxonomy = setTaxonomy
    self.render = _render

    return self
  }

  function _getParameterSetter (key) {
    return (value) => { self[key] = value }
  }

  function setTaxonomy(value) {
    self._settings = value
    self._categoryColorScale = d3.scaleOrdinal()
      .domain(value.taxonomy.map(x => x.name))
      .range(value.taxonomy.map(x => x.color))
  }

  function _renderLegend (bbox, container) {
    const legend = d3.select(container).select('g.legend')
    const legendNode = legend.node()
    const labels = self._categoryColorScale.domain().map(x => _shorttenedLabel(x + ''))
    const maxLabelLength = labels.reduce((max, x) => max > x.length ? max : x.length, 0)
    const shapeWidth = Math.max(10, maxLabelLength * 6)

    const legendOrdinal = d3.legendColor()
      .orient('horizontal')
      .shape('path', d3.symbol().type('rect'))
      .shapeWidth(shapeWidth)
      .shapePadding(10)
      .labelAlign('middle')
      .cellFilter(function (d) { return d.label !== 'e' })
      .labels(labels)
      .scale(self._categoryColorScale)

    legend.call(legendOrdinal)
    d3.select(container).select('g.legend')
      .attr('transform', `translate(${bbox.x}, ${bbox.y})`)
  }

  function _shorttenedLabel (label, maxLabelLength = 16) {
    if (label.length <= maxLabelLength) { return label }

    const fragmentLength = Math.trunc(maxLabelLength / 2 - 2)
    const startFragment = label.slice(0, fragmentLength)
    const endFragment = label.slice(label.length - fragmentLength, label.length)
    return startFragment + '...' + endFragment
  }

  function _setupHoverTooltip (container, x, y) {
    d3.select(container).select('g.hovertooltip')
      .attr('transform', `translate(${x}, ${y + self._hoverTooltipHeight - self._extraVspacing})`)
  }

  function _renderCoverageInfo(bbox, container) {

  }

  function _renderTimelineAxis(bbox, container) {
    const spacing = 10
    const xAxis = d3.axisBottom(self._xScale)
      .ticks(bbox.width / 80)
      .tickSizeOuter(0)

    const years = self._xScale.domain().map(d => new Date(d).getFullYear())
    const diff = (years[1] - years[0]) * 12

    const zoom = d3.zoom()
      .extent([[0, 0], [bbox.width, bbox.height]])
      .translateExtent([[0, -Infinity], [bbox.width, Infinity]])
      .scaleExtent([.9, diff])
      .on('zoom', args => {
          self._xScale = args.transform.rescaleX(self._originalXscale)
          const axis = d3.axisBottom(self._xScale)
            .ticks(bbox.width / 80)
            .tickSizeOuter(0)
          
          d3.select(container).select('g.axis g').call(axis)
      })

    d3.select(container).select('g.axis').selectAll('*').remove()
    d3.select(container).select('g.axis')
      .append("g")
        .attr('transform', `translate(${bbox.x}, ${bbox.y + bbox.height - spacing})`)
        .call(xAxis)
    d3.select(container).select('g.axis')
      .append('rect')
      .attr('x', bbox.x)
      .attr('y', bbox.y + bbox.height - spacing)
      .attr('height', bbox.height - spacing)
      .attr('width', bbox.width)
      .attr('fill', 'transparent')
      .call(zoom)
  }

  function _repositionTimeline(node, width){
    const xAxis = d3.axisBottom(self._xScale)
      .ticks(width / 80)
      .tickSizeOuter(0)
    node.selectAll('*').remove()
    node.call(xAxis)
  }

  function _renderTimelineEntities(bbox, container) {
    d3.select(container).select('g.entities').selectAll('*').remove()
    d3.select(container).select('g.entities')
      .append('rect')
      .attr('x', bbox.x)
      .attr('y', bbox.y)
      .attr('width', bbox.width)
      .attr('height', bbox.height)
      .attr('fill', '#FEEB71')
      .attr('stroke', '#F66C28')
  }

  function _renderAnnotationCount(bbox, container) {
    d3.select(container).select('g.details').selectAll('*').remove()
    d3.select(container).select('g.details')
      .append('rect')
      .attr('x', bbox.x)
      .attr('y', bbox.y)
      .attr('width', bbox.width)
      .attr('height', bbox.height)
      .attr('fill', '#B5E2FA')
      .attr('stroke', '#E59500')
  }

  function _renderUncertaintyLevel(bbox, container) {
    d3.select(container).select('g.details').selectAll('*').remove()
    d3.select(container).select('g.details')
      .append('rect')
      .attr('x', bbox.x)
      .attr('y', bbox.y)
      .attr('width', bbox.width)
      .attr('height', bbox.height)
      .attr('fill', '#B5E2FA')
      .attr('stroke', '#840032')
  }

  function _renderDocumentCount(bbox, container) {
    d3.select(container).select('g.details').selectAll('*').remove()
    d3.select(container).select('g.details')
      .append('rect')
      .attr('x', bbox.x)
      .attr('y', bbox.y)
      .attr('width', bbox.width)
      .attr('height', bbox.height)
      .attr('fill', '#B5E2FA')
      .attr('stroke', '#002642')
  }

  function _getDetailRender(dimension) {
    return {
      numAnnotations: _renderAnnotationCount,
      certLevel: _renderUncertaintyLevel,
      numDocuments: _renderDocumentCount,
    }[dimension]
  }

  function _getDimensions(container) {
    const height = container.clientHeight
    const width = container.clientWidth
    const freeVspace = height - (self._padding * 2)
    const freeHspace = width - (self._padding * 2)
    const freeVisVspace = (freeVspace - (self._legendHeight + self._timelineAxisHeight)) / 2

    const legendBox = {
      x: self._padding,
      y: self._padding,
      width: freeHspace,
      height: self._legendHeight
    }
    const entitiesBox = {
      x: self._padding,
      y: legendBox.y + legendBox.height,
      width: freeHspace,
      height: freeVisVspace * 2
    }
    const timelineBox = {
      x: self._padding,
      y: entitiesBox.y + entitiesBox.height,
      width: freeHspace,
      height: self._timelineAxisHeight
    }
    const detailsBox = {
      x: self._padding,
      y: timelineBox.y + timelineBox.height,
      width: freeHspace,
      height: freeVisVspace
    }

    return {legendBox, entitiesBox, timelineBox, detailsBox} 
  }

  function _getDataAndScale(data, axisWidth) {
    self._dates = data.entities.all.filter(d => Object.hasOwnProperty.call(d.properties, 'when') && d?.properties?.when !== '')
    self._datesFiltered = data.entities.filtered.filter(d => Object.hasOwnProperty.call(d.properties, 'when') && d?.propreties?.when !== '')
    self._datesUnknown = data.entities.filtered.length - self._datesFiltered.length
    
    self._xScale = d3.scaleUtc()
      .domain(d3.extent(self._dates.map(d => new Date(d.properties.when))))
      .range([0, axisWidth])
    self._originalXscale = d3.scaleUtc()
      .domain(d3.extent(self._dates.map(d => new Date(d.properties.when))))
      .range([0, axisWidth])
  }

  function _renderTimeline (data, container) {
    if(data.entities.all.length === 0) {return}
    const sectionBoundingBoxes = _getDimensions(container)
    d3.select(container).select('svg')
      .attr('width', container.clientWidth)
      .attr('height', container.clientHeight) 

    _getDataAndScale(data, sectionBoundingBoxes.timelineBox.width)
    _renderLegend(sectionBoundingBoxes.legendBox, container)
    _renderCoverageInfo(sectionBoundingBoxes.legendBox, container)
    _renderTimelineEntities(sectionBoundingBoxes.entitiesBox, container)
    _renderTimelineAxis(sectionBoundingBoxes.timelineBox, container)
    //_getDetailRender('numAnnotations')(sectionBoundingBoxes.detailsBox, container)
  }

  function _render (data, container) {
    // It takes at least 150 ms for the DOM to update and have the elements rendered
    setTimeout(() => {
      _renderTimeline(data, container)
    }, 300)
  }

  return _init()
};
