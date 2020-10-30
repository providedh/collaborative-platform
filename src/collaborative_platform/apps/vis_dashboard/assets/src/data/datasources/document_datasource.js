import { AjaxCalls } from '../../helpers'

/* Class: DocumentDatasource
 *
 *
 * */
export default function DocumentDataSource (pubSubService, appContext) {
  const self = {}

  function _init (pubSubService, appContext) {
    self._sourceName = 'document'
    self._appContext = appContext

    /**
    * Method for retrieving data.
    */
    self._source = AjaxCalls()
    self._focused = ''
    self._document = null
    self._projectVersion = 'latest'

    self.get = _getData

    pubSubService.register(self)

    self.subscribe('focus/document', ({ documentId }) => _focusDocument(documentId))

    return self
  }

  function _publishData () {
    self.publish(`data/${self._sourceName}`, _getData())
  }

  function _getData () {
    return ({
      id: self._focused,
      doc: self._document,
      html: self._document?.getElementsByTagName('text')?.[0]?.innerHTML
    })
  }

  function _focusDocument (documentId) {
    if (self._focused !== documentId) {
      self._focused = documentId
      _retrieve()
    }
  }

  /**
    * Retrieves data from the external source.
    */
  function _retrieve () {
    self.publish('status', { action: 'fetching' })
    self._source.getFile({ project: self._appContext.project, file: self._focused }, {}, null).then(response => {
      if (response.success === false) { throw (Error('Failed to retrieve files for the current project.')) }
      self._document = response.content
      self.publish('status', { action: 'fetched' })
      _publishData()
    })
  }

  return _init(pubSubService, appContext)
}
