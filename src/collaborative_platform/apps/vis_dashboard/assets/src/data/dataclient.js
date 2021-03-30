import DataService from './dataservice'
import Filter from './filter'

/**
  * class DataClient
  * Components interact with an instance of this class
  * which has a reference to the instance of the Data
  * class.
  */
export default function DataClient () {
  const self = {}

  function _init () {
    self._filters = {} // saved by dimension
    self._subscriptions = {} // saved by source

    self.subscribe = _subscribe
    self.unsubscribe = _unsubscribe
    self.filter = _filter
    self.unfilter = _unfilter
    self.focusDocument = _focus
    self.getFilter = _getFilter
    self.getFilters = _getFilters
    self.getSubscriptions = _getSubscriptions
    self.clearFilters = _clearFilters
    self.clearSubscriptions = _clearSubscriptions
    self.clearFiltersAndSubscriptions = _clearFiltersAndSubscriptions

    return self
  }

  function _getFilters () {
    return Object.keys(self._filters)
  }

  function _getFilter (dim) {
    return self._filters?.[dim]
  }

  function _getSubscriptions () {
    return Object.keys(self._subscriptions)
  }

  function _clearFilters () {
    Object.keys(self._filters).forEach(dimension => {
      _unfilter(dimension)
    })
  }

  function _clearSubscriptions () {
    Object.keys(self._subscriptions).forEach(source => {
      _unsubscribe(source)
    })
  }

  function _clearFiltersAndSubscriptions () {
    const subscriptions = Object.keys(self._subscriptions).join(', ')
    const filters = Object.keys(self._filters).join(', ')
    console.info(`Cleaning up [Subscriptions: ${subscriptions}] [Filters: ${filters}]`)
    _clearSubscriptions()
    _clearFilters()
  }

  /**
   * _subscribe
   * @param dim
      *
   */
  function _subscribe (source, callable) {
    if (!Object.hasOwnProperty.call(self._subscriptions, source)) {
      const subscription = DataService.subscribe(source, callable)

      if (subscription == null) { throw (Error('Could not subscribe to source: ' + source)) }
      self._subscriptions[source] = subscription
    } else {
      console.info('Attempted to re-subscribe to source: ' + source)
    }
  }

  /**
   * _unsubscribe
   * @param sub
   *
   */
  function _unsubscribe (source) {
    if (Object.hasOwnProperty.call(self._subscriptions, source)) {
      DataService.unsubscribe(self._subscriptions[source])
      delete self._subscriptions[source]
    } else {
      console.info('Attempted to unsubscribe from an unfollowed source: ' + source)
    }
  }

  /**
   * Receives a Filter instance and returns a copy of the Filter
   * with the
   */
  function _filter (dim, filterFunc) {
    if (Object.hasOwnProperty.call(self._filters, dim)) { DataService.unfilter(self._filters[dim]) }

    const activeFilters = self._filters[dim] // eslint-disable-line no-unused-vars
    self._filters[dim] = Filter(null, null, filterFunc)
    const filter = DataService.filter(dim, filterFunc)

    if (filter == null) {
      const { [dim]: added, ...activeFilters } = self._filters
      self._filters = activeFilters
      throw (Error('Could not filter by dimension: ' + dim))
    }
    self._filters[dim] = filter
  }

  /**
   *
   */
  function _unfilter (dim) {
    if (Object.hasOwnProperty.call(self._filters, dim)) {
      const { [dim]: toremove, ...activeFilters } = self._filters
      self._filters = activeFilters
      DataService.unfilter(toremove)
    } else {
      console.info('Attempted to unfilter an already unfiltered dimension: ' + dim)
    }
  }

  /**
   * Receives a document id.
   */
  function _focus (documentId) {
    DataService.focusDocument(documentId)
  }

  return _init()
}
