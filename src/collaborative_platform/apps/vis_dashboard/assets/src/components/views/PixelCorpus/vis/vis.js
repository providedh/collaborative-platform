import * as d3 from 'd3'

import docSorting from './docSorting'
import renderLegend from './legend'
import renderCells from './cells'
import { PixelCorpusSource } from '../config'
// import renderCertainty from './certainty';

/* Class: Vis
 *
 *
 * */
export default function Vis () {
  const self = {
    _taxonomy: null,
    _docSortingCriteria: null,
    _entitySorting: null,
    _colorBy: null,
    _entityColorScale: null,
    _certaintyColorScale: null,
    _eventCallback: null,
    _padding: 10,
    _legendWidth: 150,
    _titleHeight: 60,
    _maxRowItems: 40,
    _docNameWidth: 165,
    _fontWidth: 6.5,
    _minSideLength: 5,
    _maxLabelLength: 20
  }

  function _init () {
    self.setTaxonomy = _setTaxonomy
    self.setDocSortingCriteria = _setDocSortingCriteria
    self.setEntitySortingCriteria = _getParameterSetter('_entitySortingCriteria')
    self.setColorBy = _setColorBy
    self.setEventCallback = _getParameterSetter('_eventCallback')
    self.setSource = _getParameterSetter('_source')
    self.render = _render

    return self
  }

  function _getParameterSetter (key) {
    return (value) => { self[key] = value }
  }

  function _setDocSortingCriteria (name) {
    if (Object.hasOwnProperty.call(docSorting, name)) {
      self._docSorting = docSorting[name]
    } else {
      self._docSorting = Object.values(docSorting)[0]
    }
  }

  function _setTaxonomy (taxonomy) {
    self._taxonomy = taxonomy
    self._entityColorScale = d3.scaleOrdinal()
      .domain(taxonomy.entities.map(x => x.name))
      .range(taxonomy.entities.map(x => x.color))

    self._certaintyColorScale = d3.scaleOrdinal()
      .domain(taxonomy.taxonomy.map(x => x.name))
      .range(taxonomy.taxonomy.map(x => x.color))
  }

  function _setColorBy (colorBy) {
    self._colorBy = colorBy
  }

  function _render (container, svg, data, source) {
    if (svg == null || data == null || data == null) { return }

    svg.setAttribute('width', container.clientWidth)
    svg.setAttribute('height', container.clientHeight)

    const fileAccessor = source === PixelCorpusSource.certainty
      ? x => x.file
      : x => x.file_name
    const docOrder = self._docSorting(data.filtered, fileAccessor)
    self._docNameWidth = Math.min(self._maxLabelLength, Math.max(...Object.keys(docOrder).map(x=>x.length))) * self._fontWidth;
    const freeSpace = container.clientWidth - (self._padding * 4 + self._legendWidth + self._docNameWidth)

    // if(source===PixelCorpusSource.certainty)
    // console.log(data.filtered, docOrder, source)

    if (data.filtered.length > 0) {
      renderCells(Object.assign({}, self, { svg, source, docOrder, freeSpace, data, fileAccessor }))
    }

    // console.log(self._certaintyColorScale)

    if (source === PixelCorpusSource.certainty) {
      renderLegend(svg, self._legendWidth, self._padding, self._certaintyColorScale, source)
    } else {
      renderLegend(svg, self._legendWidth, self._padding, self._entityColorScale, source)
    }
  }

  return _init()
}
