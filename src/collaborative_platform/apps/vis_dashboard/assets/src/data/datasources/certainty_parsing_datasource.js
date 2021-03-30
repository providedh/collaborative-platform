import crossfilter from 'crossfilter2'

import { AjaxCalls } from '../../helpers'

/* Class: CertaintyDataSource
 *
 *
 * */
export default function CertaintyDataSource (pubSubService, appContext) {
  const self = {}

  function _init (pubSubService, appContext) {
    self._sourceName = 'certainty'

    self._data = crossfilter([])
    self._textDimension = self._data.dimension(x => x.textContext)
    self._categoryDimension = self._data.dimension(x => x.category)
    self._locusDimension = self._data.dimension(x => x.locus)
    self._degreeDimension = self._data.dimension(x => x.degree)
    self._certDimension = self._data.dimension(x => x.cert)
    self._respDimension = self._data.dimension(x => x.resp)
    self._matchDimension = self._data.dimension(x => x.match)
    self._idDimension = self._data.dimension(x => x['xml:id'])
    self._targetDimension = self._data.dimension(x => x.target)
    self._assertedValueDimension = self._data.dimension(x => x.assertedValue)
    self._fileDimension = self._data.dimension(x => x.file)

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
    self.subscribe('filter/certaintyCategory', args => _filterDimension(self._categoryDimension, args.filter))
    self.subscribe('filter/certaintyLocus', args => _filterDimension(self._locusDimension, args.filter))
    self.subscribe('filter/certaintyDegree', args => _filterDimension(self._degreeDimension, args.filter))
    self.subscribe('filter/certaintyCert', args => _filterDimension(self._certDimension, args.filter))
    self.subscribe('filter/certaintyMatch', args => _filterDimension(self._matchDimension, args.filter))
    self.subscribe('filter/certaintyId', args => _filterDimension(self._idDimension, args.filter))
    self.subscribe('filter/certaintyAssertedValue', args => _filterDimension(self._assertedValueDimension, args.filter))
    self.subscribe('filter/certaintyAuthor', args => _filterDimension(self._respDimension, args.filter))
    self.subscribe('filter/author', args => _filterDimension(self._respDimension, args.filter))
    self.subscribe('filter/entityId', args => _filterDimension(self._targetDimension, args.filter))
    self.subscribe('filter/fileId', args => _filterDimension(self._fileDimension, args.filter))

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

  function _getAnnotationObjects (obj) {
    const hierarchy = ['profileDesc', 'textClass', 'classCode', 'certainty']
    // Transverse the object returning the next value or null if it doesn't match
    const annotations = hierarchy.reduce((ac, dc) =>
      ac === null
        ? ac
        : (Object.hasOwnProperty.call(ac, dc) ? ac[dc] : null), obj)
    return annotations
  }

  function _processAnnotation (annotation) {
    function trimAttrName (name) {
      if (name === '@ana') { return 'category' } else { return name.startsWith('@') ? name.slice(1) : name }
    }

    const trimmedAttributes = Object.entries(annotation)
      .map(([attrName, attrValue]) => [trimAttrName(attrName), attrValue])
    const newAnnotation = Object.fromEntries(trimmedAttributes)

    if (Object.hasOwnProperty.call(newAnnotation, 'category')) {
      newAnnotation.category = newAnnotation.category
        .split(' ')
        .map(x => x.split('#')[1])
    }

    return newAnnotation
  }

  function _processData (obj, file) {
    const annotations = _getAnnotationObjects(obj)
      .map(x => Object.assign({}, _processAnnotation(x), { file }))

    return annotations
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
      self._source.getFileMeta({ project: self._appContext.project, file }, {}, null).then(response => {
        if (response.success === false) { console.info('Failed to retrieve annotations for file: ' + file) } else {
          // console.log(response.content)
          self._data.add(_processData(response.content, +file))
          _publishData()
        }
        if (++retrieved === retrieving) {
          self.publish('status', { action: 'fetched' })
        }
      })
    })
  }

  return _init(pubSubService, appContext)
}
