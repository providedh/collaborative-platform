import * as d3_ from 'd3'
import * as d3Legend from 'd3-svg-legend'
import * as topojson from "topojson-client"

import versor from './jake_low_versor.js'
import world from './land-50m.json'

const d3 = Object.assign({}, d3_, d3Legend)

import {dimOptions} from '../config'

/* Class: Map
 *
 *
 * */
export default function Map () {
  const self = {
    _eventCallback: null,
    _padding: 10,
    _legendHeight: 120,
    _mapAxisHeight: 120,
    _mainMap: {width:null, height:null, projection:null},
    _miniMap: {width:null, height:null, projection:null},
    //_extraVspacing: 50,
  }

  function _init () {
    self.setEventCallback = _getParameterSetter('_eventCallback')
    self.setTaxonomy = setTaxonomy
    self.render = _render

    return self
  }

  const land = topojson.feature(world, world.objects.land)

  const getLambda = width => d3.scaleLinear()
    .domain([0, width])
    .range([-180, 180])

  const getPhi = height => d3.scaleLinear()
    .domain([0, height])
    .range([90, -90])

  function addDragCallbacks(canvas, onDrag) {
    canvas
      .on('mousedown', () => canvas.on('mousemove', onDrag))
      .on('mouseup', () => canvas.on('mousemove', null))
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

  function renderMap (canvas, land, mapConf, dpi = 1, outline = true, graticule = true) {
    const outlineShape = {type: 'Sphere'}
    
    canvas
      .attr('height', mapConf.height * dpi)
      .attr('width', mapConf.width * dpi)
    const context = canvas.node().getContext('2d')
    const path = d3.geoPath(mapConf.projection, context)
    
    context.clearRect(0, 0, mapConf.width, mapConf.height);
      
    if (outline) { drawPathInMap(context, path, outlineShape, {fill: false, stroke: '#22333b', clip: true}) }
    
    if (graticule) { drawPathInMap(context, path, d3.geoGraticule10(), {fill: false, lineWidth: .2}) }

    drawPathInMap(context, path, land, {fill: '#c6ac8f', stroke: '#5e503f'})
    
    if (outline) { drawPathInMap(context, path, outlineShape, {fill: false, stroke: '#22333b'}) }
    
    return canvas
  }

  function getVisibleTile(extent, projection) {
    console.log(extent)
    const size = (extent[1][0] - extent[0][0]) / (2 ** z);
    const epsilon = 0.001;
    
    const x0 = x * size + epsilon,
          y0 = y * size + epsilon,
          x1 = (x + 1) * size - epsilon,
          y1 = (y + 1) * size - epsilon;

    const step = Math.min(size, 1);
    
    const tile = {
      type: "Polygon",
      coordinates: [
        []
        // Interpolate along each of the four edges of the Mercator polygon. This is a rather
        // crude way to do interpolation (with a constant step size) but it's easier than the
        // adaptive resampling that d3 does natively, which is not available to us here since
        // we're not using a projection.
        .concat(d3.range(x0, x1 + step / 2, +step).map(x => [x, y0]))
        .concat(d3.range(y0, y1 + step / 2, +step).map(y => [x1, y]))
        .concat(d3.range(x1, x0 - step / 2, -step).map(x => [x, y1]))
        .concat(d3.range(y1, y0 - step / 2, -step).map(y => [x0, y]))
        // convert this mercator polygon to a spherical polygon on the Earth
        .map(point => projection.invert(point))
      ],
    };

    return tile
  }

  function renderDraggableMap (...args) {
    const [canvas, land, mapConf, minimapConf, ...rest] = args
    let _projection = mapConf.projection
    let v0, q0, r0;
    
    function dragstarted() {
      v0 = versor.cartesian(_projection.invert(d3.mouse(this)));
      q0 = versor(r0 = _projection.rotate());
      //renderMap(canvas, land, {...mapConf, projection: _projection}, ...rest)
    }
    
    function dragged() {
      const v1 = versor.cartesian(_projection.rotate(r0).invert(d3.mouse(this)));
      const q1 = versor.multiply(q0, versor.delta(v0, v1));
      _projection = _projection.rotate(versor.rotation(q1));
      console.log(getVisibleTile(minimapConf.projection.clipExtent(), _projection))
      renderMap(canvas, land, {...mapConf, projection: _projection}, ...rest)
    }
    
    renderMap(canvas, land, {...mapConf, projection: _projection}, ...rest)
    canvas.call(
      d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
    );
    return args[0]
  }

  function drawPathInMap(context, path, shape, args={fill: 'white', stroke: 'black', lineWidth: 1, clip: false}) {
    context.save()
    context.beginPath()
    path(shape)
    if (args.clip === true) { context.clip() }
    context.lineWidth = args.lineWidth
    if (args.stroke !== false) {
      context.strokeStyle = args.stroke
      context.stroke()
    }
    if (args.fill !== false) {
      context.fillStyle = args.fill
      context.fill()
    }
    
    context.restore()
  }

  function getProjectionAndDimensions(projection, width) {
    const outlineShape = {type: 'Sphere'}
    const [[x0, y0], [x1, y1]] = d3.geoPath(projection.fitWidth(width, outlineShape)).bounds(outlineShape)
    const dy = Math.ceil(y1 - y0)
    const l = Math.min(Math.ceil(x1 - x0), dy)
    projection.scale(projection.scale() * (l - 1) / l).precision(0.2)
    return [projection, [width, dy]]
  }

  function _getDimensions(container) {
    const height = container.clientHeight
    const width = container.clientWidth
    const freeVspace = height - (self._padding * 2)
    const freeHspace = width - (self._padding * 2)
    const freeVisVspace = (freeVspace - (self._legendHeight + self._mapAxisHeight)) / 2
/*
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
      height: freeVisVspace
    }
    const MapBox = {
      x: self._padding,
      y: entitiesBox.y + entitiesBox.height,
      width: freeHspace,
      height: self._mapAxisHeight
    }
    const detailsBox = {
      x: self._padding,
      y: MapBox.y + MapBox.height,
      width: freeHspace,
      height: freeVisVspace
    }*/

    return {height, width, freeVspace, freeHspace} 
  }

  function _renderMap (data, dimension, mainMapRef, miniMapRef) {
    const boundingBoxes = _getDimensions(mainMapRef.parentElement.parentElement)
    /*const sectionBoundingBoxes = _getDimensions(dimension, container)
    d3.select(container).select('svg')
      .attr('width', container.clientWidth)
      .attr('height', container.clientHeight) 

    _renderLegend(sectionBoundingBoxes.legendBox, container)
    _renderCoverageInfo(sectionBoundingBoxes.legendBox, container)
    _renderMapEntities(sectionBoundingBoxes.entitiesBox, container)
    _renderMapAxis(sectionBoundingBoxes.MapBox, container)
    _getDetailRender(dimension)(sectionBoundingBoxes.detailsBox, container)*/
    const mainMapRadius = Math.min(2*(boundingBoxes.width/3) - boundingBoxes.width*.1, boundingBoxes.height - 30)
    const [mainmapProjection, [mainmapWidth, mainmapHeight]] = getProjectionAndDimensions(d3.geoOrthographic(), mainMapRadius)
    self._mainMap = {projection: mainmapProjection, width: mainmapWidth, height: mainmapHeight}

    const [minimapProjection, [minimapWidth, minimapHeight]] = getProjectionAndDimensions(d3.geoEqualEarth().clipExtent([[0, 0], [boundingBoxes.width/3, boundingBoxes.width/3]]), boundingBoxes.width/3)
    self._miniMap = {projection: minimapProjection, width: minimapWidth, height: minimapHeight}

    renderDraggableMap(d3.select(mainMapRef), land, self._mainMap, self._miniMap)
    renderMap(d3.select(miniMapRef), land, self._miniMap, 1, true, false)
  }

  function _render (data, dimension, mainMapRef, miniMapRef) {
    // It takes at least 150 ms for the DOM to update and have the elements rendered
    setTimeout(() => {
      _renderMap(data, dimension, mainMapRef, miniMapRef)
    }, 300)
  }

  return _init()
};
