import crossfilter from 'crossfilter2'
import { AjaxCalls } from '../../helpers'
/* Class: CertaintyDataSource


 */
export default function CertaintyDataSource (pubSubService, appContext) {
  const self = {}
  function _init (pubSubService, appContext) {
    self._sourceName = 'certainty'
    self._data = crossfilter([])

    self._assertedValueDimension = self._data.dimension(x => x.assertedValue)
    self._categoriesDimension = self._data.dimension(x => x.categories)
    self._certDimension = self._data.dimension(x => x.cert)
    self._degreeDimension = self._data.dimension(x => x.degree)
    self._descDimension = self._data.dimension(x => x.desc)
    self._locusDimension = self._data.dimension(x => x.locus)
    self._matchDimension = self._data.dimension(x => x.match)
    self._respDimension = self._data.dimension(x => x.resp)
    self._targetDimension = self._data.dimension(x => x.target)
    self._idDimension = self._data.dimension(x => x['xml:id'])
    self._fileidDimension = self._data.dimension(x => x.file_id)
    self._filenameDimension = self._data.dimension(x => x.filename)

    self._appContext = appContext
    /**
    * Method for retrieving data.
    */
    self._source = AjaxCalls()
    /**
    * This options allow recreating the state.
    * They are used to query for the data and take into
    * account applied filters.
    */
    self._options = {}
    self._fetched = false
    self.get = _getData
    pubSubService.register(self)

    // common filters
    self.subscribe(`filter/entityId`, args=>_filterDimension(self._targetDimension, args.filter))
    self.subscribe(`filter/fileName`, args=>_filterDimension(self._filenameDimension, args.filter))
    self.subscribe(`filter/fileId`, args=>_filterDimension(self._fileidDimension, args.filter))

    self.subscribe(`filter/categories`, args=>_filterDimension(self._categoriesDimension, args.filter))
    self.subscribe(`filter/locus`, args=>_filterDimension(self._locusDimension, args.filter))
    self.subscribe(`filter/match`, args=>_filterDimension(self._matchDimension, args.filter))
    self.subscribe(`filter/resp`, args=>_filterDimension(self._respDimension, args.filter))
    self.subscribe(`filter/assertedValue`, args=>_filterDimension(self._assertedValueDimension, args.filter))
    self.subscribe(`filter/degree`, args=>_filterDimension(self._degreeDimension, args.filter))
    self.subscribe(`filter/cert`, args=>_filterDimension(self._certDimension, args.filter))
    self.subscribe(`filter/certId`, args=>_filterDimension(self._idDimension, args.filter))

    return self
  }
  function _publishData () {
    const data = { all: self._data.all(), filtered: self._data.allFiltered() }
    self.publish(`data/${self._sourceName}`, data)
  }
  function _handleAction (args) {
    _filter(args.dim, args.filter)
  }
  function _getData () {
    if (self._fetched === false) {
      self._fetched = true
      _retrieve()
    }
    return ({ all: self._data.all(), filtered: self._data.allFiltered() })
  }
  /**
    * Handles filtering for the selected dimension. Depending on the dimension
    * and type of filtering, this will be done through crossfiltering or by retrieving
    * data with query parameters.
    *
    * If new data is retrieved, crossfilter filters must be preserved.
    *
    * If the filtering function is null, then the filter is deleted.
    *
    * @param dimension
    *
    * @param args
    *
    */
  function _filterDimension (dimension, filter) {
    if (filter === null) dimension.filterAll()
    else dimension.filterFunction(filter)
    _publishData()
  }
  function _processData (data, fileId) {
    const filename = self._appContext.id2document[fileId].name
    return data.map(d => {
      const {ana, target, locus, ...annotation} = d
      const categories = ana.length === 0 ? ['no category'] : ana.split(' ').map(c => c.split('#')[1])

      return {
        categories,
        filename,
        file_id: +fileId,
        target: target.slice(1),
        locus: d.match !== null ? 'attribute' : locus,
        ...annotation}
    })
  }
  /**
    * Retrieves data from the external source.
    */
  function _retrieve () {
    const files = Object.keys(self._appContext.id2document)
    let retrieved = 0; const retrieving = files.length
    self.publish('status', { action: 'fetching' })
    self._data.remove(() => true) // clear previous data
    files.forEach(file => {
      self._source.getAnnotations({ project: self._appContext.project, file }, {}, null).then(response => {
        if (response.success === false) { console.info('Failed to retrieve entities for file: ' + file) } else {
          self._data.add(_processData(response.content, file))
          _publishData()
        }
        if (++retrieved == retrieving) {
          self.publish('status', { action: 'fetched' })
        }
      })
    })
  }
  return _init(pubSubService, appContext)
}
