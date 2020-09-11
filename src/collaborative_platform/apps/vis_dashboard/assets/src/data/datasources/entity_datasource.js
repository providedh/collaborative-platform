import crossfilter from 'crossfilter2'

import { AjaxCalls } from '../../helpers'

/* Class: EntityDataSource
 *
 *
 * */
export default function EntityDataSource (pubSubService, appContext) {
  const self = {}

  function _init (pubSubService, appContext) {
    self._sourceName = 'entity'

    self._data = crossfilter([])
    self._idDimension = self._data.dimension(x => x.id)
    self._nameDimension = self._data.dimension(x => x.name)
    self._typeDimension = self._data.dimension(x => x.type)
    self._docNameDimension = self._data.dimension(x => x.file_name)
    self._docIdDimension = self._data.dimension(x => x.file_id)
    self._propertiesDimension = self._data.dimension(x => x.properties)
    self._propertyKeysDimension = self._data.dimension(x => Object.keys(x.properties))

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

    self.subscribe('filter/entityId', args => _filterDimension(self._idDimension, args.filter))
    self.subscribe('filter/entityProperties', args => _filterDimension(self._propertyDimension, args.filter))
    self.subscribe('filter/entityPropertyKeys', args => _filterDimension(self._propertyKeysDimension, args.filter))
    self.subscribe('filter/entityName', args => _filterDimension(self._nameDimension, args.filter))
    self.subscribe('filter/entityType', args => _filterDimension(self._typeDimension, args.filter))
    self.subscribe('filter/fileName', args => _filterDimension(self._docNameDimension, args.filter))
    self.subscribe('filter/fileId', args => _filterDimension(self._docIdDimension, args.filter))

    return self
  }

  function _publishData () {
    const data = { all: self._data.all(), filtered: self._data.allFiltered() }
    self.publish(`data/${self._sourceName}`, data)
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
      return Object.assign({},
        {file_id: +fileId, filename, ...d },
        {properties: Object.keys(d.properties).length === 0 ? {'no properties': 'no properties'} : d.properties},
        {id: `${d.type}-${d.id}`})
    })
  }

  /**
    * Retrieves data from the external source.
    */
  function _retrieve () {
    const files = Object.keys(self._appContext.id2document)
    const getName = fileId => self._appContext.id2document[fileId].name
    let retrieved = 0; const retrieving = files.length

    self.publish('status', { action: 'fetching' })
    self._data.remove(() => true) // clear previous data
    files.forEach(file => {
      self._source.getFileEntities({ project: self._appContext.project, file }, {}, null).then(response => {
        if (response.success === false) {
          console.info('Failed to retrieve entities for file: ' + file)
        } else {
          self._data.add(_processData(response.content, file))
        }
        _publishData()
        if (++retrieved === retrieving) {
          self.publish('status', { action: 'fetched' })
        }
      })
    })
  }

  return _init(pubSubService, appContext)
}
