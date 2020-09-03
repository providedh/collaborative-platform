import * as d3_ from 'd3'
import * as d3Legend from 'd3-svg-legend'
import * as topojson from "topojson-client"

import versor from './jake_low_versor.js'
import highResWorld from './land-50m.json'
import lowResWorld from './land-110m.json'
import zoom from './versor_zooming'

const d3 = Object.assign({}, d3_, d3Legend)

import {dimOptions} from '../config'

/* Class: Map
 *
 *
 * */
export default function Map () {
  const self = {};

  function init() {
    function getParameterSetter (key) {
      return (value) => { self[key] = value }
    }

    self._padding = 10

    self._assets = {
      lowResWorld: topojson.feature(lowResWorld, lowResWorld.objects.land),
      highResWorld: topojson.feature(highResWorld, highResWorld.objects.land),
      reticule: d3.geoGraticule10(),
      outlineShape: {type: 'Sphere'}
    }

    self.setEventCallback = getParameterSetter('_eventCallback')
    self.setTaxonomy = getParameterSetter('_taxonomy')

    // It takes at least 150 ms for the DOM to update and have the elements rendered
    self.render = (...args) => setTimeout(() => render(...args), 500)

    const canvasConf = {width: null, height: null, projection: null, d3path: null}
    self._mainMap = {...canvasConf}
    self._miniMap = {...canvasConf}
    self._miniMapOverlay = {...canvasConf}

    return self
  }

  function drawPathInMap (context, path, shape, args={fill: 'white', stroke: 'black', lineWidth: 1, clip: false}) {
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

  function renderMap (canvasConf, land, graticule = true) {
    canvasConf.context.clearRect(0, 0, canvasConf.width, canvasConf.height);
      
    drawPathInMap( // 1. Outline
      canvasConf.context,
      canvasConf.d3path,
      self._assets.outlineShape,
      {fill: false, stroke: '#22333b', clip: true})
    if (graticule) {
      drawPathInMap( // 2. ?reticule
        canvasConf.context, 
        canvasConf.d3path, 
        self._assets.reticule, 
        {fill: false, lineWidth: .2}) 
    }
    drawPathInMap( // 3. Land
      canvasConf.context, 
      canvasConf.d3path, 
      land, 
      {fill: '#c6ac8f', stroke: '#5e503f'})
    drawPathInMap( // 4. Outline
      canvasConf.context,
      canvasConf.d3path,
      self._assets.outlineShape,
      {fill: false, stroke: '#22333b', clip: true})
  }

  function getProjectionAndDimensions (projection, width) {
    const outlineShape = {type: 'Sphere'}
    const [[x0, y0], [x1, y1]] = d3.geoPath(projection.fitWidth(width, outlineShape)).bounds(outlineShape)
    const dy = Math.ceil(y1 - y0)
    const l = Math.min(Math.ceil(x1 - x0), dy)
    projection.scale(projection.scale() * (l - 1) / l).precision(0.2)
    return [projection, [width, dy]]
  }

  function getDimensions (container) {
    const height = container.clientHeight
    const width = container.clientWidth
    const freeVspace = height - (self._padding * 2)
    const freeHspace = width - (self._padding * 2)
    const freeVisVspace = (freeVspace - (self._legendHeight + self._mapAxisHeight)) / 2
    const mainMapRadius = Math.min(2*(width/3) - width*.1, height - 30)
    const miniMapWidth = width / 3
    const miniMapClipExtent = [[0, 0], [width/3, width/3]]

    return {height, width, freeVspace, freeHspace, mainMapRadius, miniMapWidth, miniMapClipExtent}
  }

  function setupInteractions () {
    function zoomed(args) {
      const { k, x, y } = currentEvent;
      const scale = self._mainMap.projection._scale === undefined
        ? (self._mainMap.projection._scale = self._mainMap.projection.scale())
        : self._mainMap.projection._scale

      const translate = self._mainMap.projection
        .translate()
        .map(d => d / (self._mainMap.projection.scale() / scale))
      self._mainMap.projection
        .scale(k)
        .translate([
          translate[0] * (k / scale) + x,
          translate[1] * (k / scale) + y
        ]);
      renderMap(self._mainMap, self._assets.lowResWorld, false)
    }

    self._mainMap.selection
      .call(zoom(self._mainMap.projection)
        .on("zoom.render", () => renderMap(self._mainMap, self._assets.lowResWorld, false))
        .on("end.render", () => renderMap(self._mainMap, self._assets.highResWorld)))
  }

  function render (data, dimension, mainMapRef, miniMapRef, miniMapOverlayRef) {
    if (mainMapRef === undefined) { return }
    const bboxes = getDimensions(mainMapRef.parentElement.parentElement)

    const [mainMapProjection, [mainMapWidth, mainMapHeight]] = 
      getProjectionAndDimensions(d3.geoOrthographic(), bboxes.mainMapRadius)

    const [miniMapProjection, [miniMapWidth, miniMapHeight]] = 
      getProjectionAndDimensions(d3.geoEqualEarth().clipExtent(bboxes.miniMapClipExtent), bboxes.miniMapWidth)

    self._mainMap = {
      selection: d3.select(mainMapRef),
      context: mainMapRef.getContext('2d'),
      width: mainMapWidth,
      height: mainMapHeight,
      projection: mainMapProjection,
      d3path: d3.geoPath(mainMapProjection, mainMapRef.getContext('2d'))
    }

    self._miniMap = {
      selection: d3.select(miniMapRef),
      context: miniMapRef.getContext('2d'),
      width: miniMapWidth,
      height: miniMapHeight,
      projection: miniMapProjection,
      d3path: d3.geoPath(miniMapProjection, miniMapRef.getContext('2d'))
    }

    self._miniMapOverlay = {
      selection: d3.select(miniMapOverlayRef),
      context: miniMapOverlayRef.getContext('2d'),
      width: miniMapWidth,
      height: miniMapHeight,
      projection: miniMapProjection,
      d3path: d3.geoPath(miniMapProjection, miniMapOverlayRef.getContext('2d'))
    }

    self._mainMap.selection
      .attr('height', self._mainMap.height)
      .attr('width', self._mainMap.width)

    self._miniMap.selection
      .attr('height', self._miniMap.height)
      .attr('width', self._miniMap.width)

    self._miniMapOverlay.selection
      .attr('height', self._miniMapOverlay.height)
      .attr('width', self._miniMapOverlay.width)

    renderMap(self._mainMap, self._assets.highResWorld)
    renderMap(self._miniMap, self._assets.lowResWorld, false)
    setupInteractions()
  }

  return init();
};
