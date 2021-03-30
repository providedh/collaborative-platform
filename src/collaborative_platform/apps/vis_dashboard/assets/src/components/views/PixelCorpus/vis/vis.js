import * as d3 from 'd3'

import docSorting from './docSorting'
import renderLegend from './legend'
import renderCells from './cells'
import {PixelCorpusSortBy, PixelCorpusColorBy, PixelCorpusSource} from '../config'
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
    self.render = (...args) => setTimeout(() => _render(...args), 700)

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
  }

  function _setColorBy (colorBy) {
    self._colorBy = colorBy

    self._entityColorScale = d3.scaleOrdinal()
        .domain(self._taxonomy.entities.map(x => x.name))
        .range(self._taxonomy.entities.map(x => x.color))

    if (self._colorBy === 'author') {
      self._certaintyColorScale = d3.scaleOrdinal()
          .range(d3.schemeTableau10)
    }

    switch (self._colorBy) {
      case PixelCorpusColorBy.type:
        self._certaintyColorScale = d3.scaleOrdinal()
          .range(d3.schemeTableau10)
      break
      case PixelCorpusColorBy.category:
        self._certaintyColorScale = d3.scaleOrdinal()
          .range(d3.schemeTableau10)
      break
      case PixelCorpusColorBy.certaintyLevel:
        self._certaintyColorScale = d3.scaleOrdinal()
          .domain(self._taxonomy.taxonomy.map(x => x.name))
          .range(self._taxonomy.taxonomy.map(x => x.color))
      break
      case PixelCorpusColorBy.authorship:
        self._certaintyColorScale = d3.scaleOrdinal()
          .range(d3.schemeTableau10)
      break
      case PixelCorpusColorBy.entity:
        self._certaintyColorScale = d3.scaleOrdinal()
          .range(d3.schemeTableau10)
      break
      case PixelCorpusColorBy.locus:
        self._certaintyColorScale = d3.scaleOrdinal()
          .range(d3.schemeTableau10)
      break
    }
  }

  function _render (container, svg, data, source) {
    if (svg == null || data == null || data == null) { return }

    svg.setAttribute('width', container.clientWidth)
    svg.setAttribute('height', container.clientHeight)

    const fileAccessor = x => x.filename
    const docOrder = self._docSorting(data.filtered, fileAccessor)
    self._docNameWidth = Math.min(self._maxLabelLength, Math.max(...Object.keys(docOrder).map(x => x.length))) * self._fontWidth
    const freeSpace = container.clientWidth - (self._padding * 4 + self._legendWidth + self._docNameWidth)

    // if(source===PixelCorpusSource.certainty)
    // console.log(data.filtered, docOrder, source)

    const _colorScale = source === PixelCorpusSource.certainty ? self._certaintyColorScale : self._entityColorScale
    renderCells(Object.assign({}, self, { svg, source, docOrder, freeSpace, data, fileAccessor, _colorScale}))

    // console.log(self._certaintyColorScale)

    if (source === PixelCorpusSource.certainty) {
      renderLegend(svg, self._legendWidth, self._padding, self._certaintyColorScale, source)
    } else {
      renderLegend(svg, self._legendWidth, self._padding, self._entityColorScale, source)
    }
  }

  return _init()
}
