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

  function getBounds (projection) {
    const path = d3.geoPath(projection),
      sphere = path({ type: "Sphere" })
        .replace(/^M|Z$/g, "")
        .split(/L/)
        .map(d => d.split(",").map(Number));
    sphere.push(sphere[0]);
    const coordinates = [];
    for (const [p, q] of d3.pairs(sphere)) {
      const D = Math.hypot(p[0], q[0], p[1] - q[1]),
        pt = d3.interpolateArray(p, q);
      for (let i = 0; i < D; i += 5) {
        const r = projection.invert(pt(i / D));
        coordinates.push([r[0] + 360, r[1]]);
      }
    }

    let points = {
        type: "MultiPoint",
        coordinates: coordinates.map(d => [
          ((d[0] + 360 + 180) % 360) - 180,
          d[1]
        ])
      },
      bb = d3.geoBounds(points),
      [[w, s], [e, n]] = bb,
      c = d3.geoCentroid(points);

    // poles
    if (path({ type: "Point", coordinates: [0, 90] })) {
      n = 90;
      e = w = 180;
      c = 0;
    }
    if (path({ type: "Point", coordinates: [0, -90] })) {
      s = -90;
      e = w = 180;
      c = 0;
    }

    return c[0] >= w && c[0] <= e ? [[w, s], [e, n]] : [[w, s], [e + 360, n]];
  }

  function updateBounds (projection) {
    const b = getBounds(self._mainMap.projection)
    
    const x0 = Math.min(b[0][0], b[1][0])
    const x1 = Math.max(b[0][0], b[1][0])
    const y0 = Math.max(b[0][1], b[1][1])
    const y1 = Math.min(b[0][1], b[1][1])

    self._bounds = {x0, y0, x1, y1}
  }

  function renderVisible () {
    updateBounds(self._mainMap.projection)

    const viewportAreaPath = {
      type: "LineString",
      coordinates: [
        [self._bounds.x0, self._bounds.y0],
        [(self._bounds.x0 + self._bounds.x1)/2, self._bounds.y0],
        [self._bounds.x1, self._bounds.y0],
        [self._bounds.x1, self._bounds.y1],
        [(self._bounds.x0 + self._bounds.x1)/2, self._bounds.y1],
        [self._bounds.x0, self._bounds.y1],
        [self._bounds.x0, self._bounds.y0],
      ]
    }

    //console.info(JSON.stringify(viewportAreaPath))

    self._miniMapOverlay.context.clearRect(0, 0, self._miniMapOverlay.width, self._miniMapOverlay.height);
    drawPathInMap( // 1. Outline
      self._miniMapOverlay.context,
      self._miniMapOverlay.d3path,
      viewportAreaPath,
      {fill: false, stroke: 'red', clip: true, lineWidth: 2})
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
    projection.scale(projection.scale() * (l - 1) / l).precision(0.2).clipExtent([[x0, x0], [x1, y1]])
    return [projection, [width, dy]]
  }

  function getDimensions (container) {
    const height = container.clientHeight
    const width = container.clientWidth
    const freeVspace = height - (self._padding * 2)
    const freeHspace = width - (self._padding * 2)
    const freeVisVspace = (freeVspace - (self._legendHeight + self._mapAxisHeight)) / 2
    const mainMapRadius = Math.min(2*(width/3) - width*.1, height - 30) - 10
    const miniMapWidth = Math.min(Math.max(220, (width / 3)), 350) - 10

    return {height, width, freeVspace, freeHspace, mainMapRadius, miniMapWidth}
  }

  function setupInteractions () {
    self._mainMap.selection
      .call(zoom(self._mainMap.projection)
        .on("zoom.render", () => {
          renderMap(self._mainMap, self._assets.lowResWorld, false)
          renderVisible()
        })
        .on("end.render", () => {
          renderMap(self._mainMap, self._assets.highResWorld)
          renderVisible()
      }))
  }

  function render (data, dimension, mainMapRef, miniMapRef, miniMapOverlayRef, tableRef) {
    if (mainMapRef === undefined) { return }
    const bboxes = getDimensions(mainMapRef.parentElement.parentElement)

    const [mainMapProjection, [mainMapWidth, mainMapHeight]] = 
      getProjectionAndDimensions(d3.geoOrthographic(), bboxes.mainMapRadius)

    const [miniMapProjection, [miniMapWidth, miniMapHeight]] = 
      getProjectionAndDimensions(d3.geoEqualEarth(), bboxes.miniMapWidth)



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
      .style('top', '10px')
      .style('right', '10px')
      .attr('height', self._miniMap.height)
      .attr('width', self._miniMap.width)

    self._miniMapOverlay.selection
      .style('top', '10px')
      .style('right', '10px')
      .attr('height', self._miniMapOverlay.height)
      .attr('width', self._miniMapOverlay.width)

    d3.select(tableRef)
      .style('top', (self._miniMapOverlay.height + 20) + 'px')
      .style('height', (bboxes.height - self._miniMapOverlay.height - 30) + 'px')

    renderMap(self._mainMap, self._assets.highResWorld)
    renderMap(self._miniMap, self._assets.lowResWorld, false)
    updateBounds(self._mainMap.projection)
    renderVisible()
    setupInteractions()
  }

  return init();
};
