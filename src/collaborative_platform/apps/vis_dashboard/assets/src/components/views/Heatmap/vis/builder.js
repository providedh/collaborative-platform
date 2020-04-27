import ColorScales from './color_scales'
import RangeScales from './range_scales'
import GridRenderers from './grid'
import AxisRenderers from './axis'
import Heatmap from './heatmap'

/* Class: Builder
 *
 *
 * */
function Builder () {
  const self = {}

  function _init () {
    _resetBuild()

    self.getResult = () => self._currentHeatmap
    self.resetBuild = _resetBuild
    self.setLayout = _setLayout
    self.setRangeScale = _setRangeScale
    self.setColorScale = _setColorScale
    self.setEventCallback = _setEventCallback

    return self
  }

  function _resetBuild () { self._currentHeatmap = Heatmap() }

  function _setLayout () {
    if (self._currentHeatmap != null) {
      self._currentHeatmap.setGridRenderer(null)
      self._currentHeatmap.setAxisRenderer(null)
    }
  }

  function _setColorScale (colorScaleName) {
    if (self._currentHeatmap != null &&
      Object.hasOwnProperty.call(ColorScales, colorScaleName)) {
      const scale = ColorScales[colorScaleName]
      self._currentHeatmap.setColorScale(scale)
    }
  }

  function _setRangeScale (rangeScaleName) {
    if (self._currentHeatmap != null &&
      Object.hasOwnProperty.call(RangeScales, rangeScaleName)) {
      const scale = RangeScales[rangeScaleName]()
      self._currentHeatmap.setRangeScale(scale)
    }
  }

  function _setEventCallback (callback) {
    if (self._currentHeatmap != null) { self._currentHeatmap.setEventCallback(callback) }
  }

  return _init()
}

/* Class: RegularHeatmapBuilder
 *
 *
 * */
function RegularHeatmapBuilder () {
  const self = Builder()

  function _init () {
    self.setLayout = _setLayout

    return self
  }

  function _setLayout () {
    if (self._currentHeatmap != null) {
      // console.log('layout', self._currentHeatmap)
      self._currentHeatmap.setGridRenderer(GridRenderers.regularGrid)
      self._currentHeatmap.setAxisRenderer(AxisRenderers.regularAxis)
    }
  }

  return _init()
}

/* Class: StairHeatmapBuilder
 *
 *
 * */
function StairHeatmapBuilder () {
  const self = Builder()

  function _init () {
    self.setLayout = _setLayout

    return self
  }

  function _setLayout () {
    if (self._currentHeatmap != null) {
      self._currentHeatmap.setGridRenderer(GridRenderers.stairGrid)
      self._currentHeatmap.setAxisRenderer(AxisRenderers.regularAxis)
    }
  }

  return _init()
}

/* Class: HeartHeatmapBuilder
 *
 *
 * */
function HeartHeatmapBuilder () {
  const self = Builder()

  function _init () {
    self.setLayout = _setLayout

    return self
  }

  function _setLayout () {
    if (self._currentHeatmap != null) {
      self._currentHeatmap.setGridRenderer(GridRenderers.tiltedGrid)
      self._currentHeatmap.setAxisRenderer(AxisRenderers.tiltedAxis)
    }
  }

  return _init()
}

export { RegularHeatmapBuilder, StairHeatmapBuilder, HeartHeatmapBuilder }
