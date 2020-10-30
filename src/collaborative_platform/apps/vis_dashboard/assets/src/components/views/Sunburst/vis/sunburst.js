import * as d3_ from 'd3'
import * as d3Legend from 'd3-svg-legend'
const d3 = Object.assign({}, d3_, d3Legend)

/* Class: Heatmap
 *
 *
 * */
export default function Sunburst () {
  const self = {
    _eventCallback: null,
    _padding: 10,
    _legendWidth: 120,
    _hoverTooltipHeight: 10,
    _extraVspacing: 50,
    _getLegendHeight: numLevels => numLevels * 0
  }

  function _init () {
    self.setEventCallback = _getParameterSetter('_eventCallback')
    self.setTaxonomy = _getParameterSetter('_settings')
    self.render = _render

    return self
  }

  function _getParameterSetter (key) {
    return (value) => { self[key] = value }
  }

  function _setupColorSchemes () {
    self._colorSchemes = {
      default: null,
      author: d3.scaleOrdinal().range(d3.schemePaired),
      document: d3.scaleOrdinal().range(d3.schemePaired),
      category: d3.scaleOrdinal()
        .range(Object.values(self._settings.taxonomy).map(x => x.color))
        .domain(Object.values(self._settings.taxonomy).map(x => x.name)),
      attribute: d3.scaleOrdinal().range(d3.schemePaired),
      degree: d3.interpolateYlOrRd,
      certainty: d3.scaleOrdinal()
        .range(d3.schemeYlOrRd[5])
        .domain(['unknown', 'very low', 'low', 'medium', 'high', 'very high'])
    }
  }

  function _renderLegend (container, x, y) {
    const legend = d3.select(container).select('g.legend')
    const legendNode = legend.node()
    const labels = self._colorSchemes.default.domain().map(x => _shorttenedLabel(x + ''))
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
      .scale(self._colorSchemes.default)

    legend.call(legendOrdinal)

    // It takes at least 150 ms for the DOM to update and have the elements rendered
    setTimeout(() => {
      const { width, height } = legendNode.getBBox()
      d3.select(container).select('g.legend')
        .attr('transform', `translate(${x - width / 2}, ${y - height - self._padding})`)
    }, 300)
  }

  function _renderInnerCircle (source, filters, annotationsCount, centerX, centerY, innerCircleRadius, container) {
    const innerText = source === 'certainty' ? 'annotations' : 'entities'

    d3.select(container).select('svg').selectAll('g.innerCircle')
      .data([annotationsCount])
      .enter().append('svg:g')
      .attr('class', 'innerCircle')
      .on('click', () => self._eventCallback({ action: 'click', target: 'unfilter' }))
      .each(function (d) {
        d3.select(this)
          .append('svg:circle')
          .attr('r', innerCircleRadius)
          .attr('cx', innerCircleRadius)
          .attr('cy', innerCircleRadius)
        d3.select(this)
          .append('svg:text')
          .attr('class', 'annotations')
          .attr('x', innerCircleRadius)
          .attr('y', innerCircleRadius - 10)
        d3.select(this)
          .append('svg:text')
          .attr('class', 'desc')
          .attr('x', innerCircleRadius)
          .attr('y', innerCircleRadius + 2)
        d3.select(this)
          .append('svg:text')
          .attr('class', 'filters')
          .attr('x', innerCircleRadius)
          .attr('y', innerCircleRadius + 16)
        d3.select(this)
          .append('svg:text')
          .attr('class', 'click')
          .attr('x', innerCircleRadius)
          .attr('y', innerCircleRadius + 28)
          .text('(click to remove)')
      })

    d3.select(container).select('svg').selectAll('g.innerCircle')
      .attr('transform', `translate(${centerX - innerCircleRadius}, ${centerY - innerCircleRadius})`)
      .style('cursor', () => filters.length > 0 ? 'pointer' : 'default')
      .each(function (d) {
        d3.select(this).select('text.annotations').text(d)
        d3.select(this).select('text.desc').text(innerText)
        d3.select(this).select('text.filters')
          .classed('d-none', filters.length === 0)
          .text('Filtering ' + filters.length + ' dimensions')
        d3.select(this).select('text.click')
          .classed('d-none', filters.length === 0)
      })
  }

  function _partition (data, radius) {
    return d3.partition().size([2 * Math.PI, radius])(
      d3.hierarchy(data, d => d.children).sum(d => d.hasOwnProperty.call(d, 'children') ? 0 : 1)
    )
  }

  function _shorttenedLabel (label, maxLabelLength = 16) {
    if (label.length <= maxLabelLength) { return label }

    const fragmentLength = Math.trunc(maxLabelLength / 2 - 2)
    const startFragment = label.slice(0, fragmentLength)
    const endFragment = label.slice(label.length - fragmentLength, label.length)
    return startFragment + '...' + endFragment
  }

  function _renderSections (data, count, levels, container, maxDiameter, centerX, centerY) {
    const root = _partition(data, maxDiameter / 2)
    root.each(d => { d.current = d })

    const arc = d3.arc()
      .startAngle(d => d.x0)
      .endAngle(d => d.x1)
      .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
      .padRadius(maxDiameter / 4)
      .innerRadius(d => d.y0)
      .outerRadius(d => d.y1 - 1)

    const g = d3.select(container).select('g.sections')
      .attr('transform', `translate(${centerX}, ${centerY})`)

    g.select('g.paths')
      .attr('fill-opacity', 0.6)
      .selectAll('path')
      .data(root.descendants().filter(d => (d.depth && d.depth <= Object.keys(levels).length)))
      .join('path')
      .attr('fill', d => { while (d.depth > 1) d = d.parent; return self._colorSchemes.default(d.data.name) })
      .attr('d', arc)
      .on('click', d => self._eventCallback({ action: 'click', ...d }))
      .on('mouseenter', d => {
        let hierarchy = [d.data.name]; let t = d
        while (t = t?.parent) hierarchy = [t.data.name, ...hierarchy] // eslint-disable-line no-cond-assign

        // remove the 'root' label
        hierarchy.shift()

        d3.select(container).select('g.hovertooltip text')
          .text(`${hierarchy.join(' > ')} (${d.value} annotations)`)
        self._eventCallback({ action: 'hover', ...d })
      })
      .on('mouseleave', d => {
        d3.select(container).select('g.hovertooltip text').text('')
      })

    g.select('g.labels')
      .selectAll('text')
      .data(root.descendants().filter(d => d.depth && d.depth <= Object.keys(levels).length && (d.y0 + d.y1) / 2 * (d.x1 - d.x0) > 10))
      .join('text')
      .attr('transform', function (d) {
        const x = (d.x0 + d.x1) / 2 * 180 / Math.PI
        const y = (d.y0 + d.y1) / 2
        return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`
      })
      .attr('dy', '0.35em')
      .text(d => _shorttenedLabel(d.data.name + ''))
  }

  function _setupHoverTooltip (container, x, y) {
    d3.select(container).select('g.hovertooltip')
      .attr('transform', `translate(${x}, ${y + self._hoverTooltipHeight - self._extraVspacing})`)
  }

  function _renderSunburst (data, count, source, filters, levels, container) {
    const height = container.clientHeight
    const width = container.clientWidth
    const freeVspace = height - (self._padding * 2 + self._hoverTooltipHeight)
    const freeHspace = width - (self._padding * 2)
    const maxDiameter = Math.min(freeHspace, freeVspace) + self._extraVspacing
    const centerX = width / 2
    const centerY = (freeVspace - (self._padding*2)) / 2 + self._padding
    const innerCircleRadius = 50

    self._colorSchemes.default = d3.scaleOrdinal(d3.quantize(d3.interpolateRainbow, data.children.length + 1))

    d3.select(container).select('svg')
      .attr('width', width)
      .attr('height', height)

    _setupHoverTooltip(container, centerX, centerY + maxDiameter / 2)
    _renderInnerCircle(source, filters, count, centerX, centerY, innerCircleRadius, container)
    _renderSections(data, count, levels, container, maxDiameter, centerX, centerY)
    _renderLegend(container, centerX, height)
  }

  function _render (data, source, levels, container) {
    const { tree, count } = data.filtered

    _setupColorSchemes()
    _renderSunburst(tree, count, source, data.filters, levels, container)
  }

  return _init()
};
