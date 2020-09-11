import $ from 'jquery'
/* Module: AjaxCalls
 * Module for building full API call urls.
 *
 * API endpoints:
 * - get_SaveUrl
 * - getAddAnnotationUrl
 * - getHistoryUrl
 * - getAutocompleteUrl
 * */
var AjaxCalls = function (args) {
  const baseUrl = [window.location.protocol + '/', window.location.hostname + ':' + window.location.port].join('/')

  // PROJECT SETTINGS
  const contributorsUrl = ({ project }) => ['/api', 'projects', project, 'contributors'].join('/')
  const settingsUrl = ({ project }) => ['/api', 'projects', project, 'settings'].join('/')
  const projectVersionsUrl = ({ project }) => ['/stats', 'project', project, 'versions'].join('/')

  // VIS DASHBOARD
  const updateUrl = ({ project, dashboard }) => ['/dashboard', 'project', project, 'vis', dashboard, 'update'].join('/')

  // STATS
  const statsUrl = ({ project, version }) => ['/stats', 'project', project, 'version', version, 'stats'].join('/')

  // CLOSE READING
  const closeHistory = ({ project, file, version }) => ['/api', 'closeReading', 'project', project, 'file', file, 'version', version, 'history'].join('/')
  const fuzzysearch = ({ project, entity, query }) => ['/fuzzysearch', 'fuzzysearch', project, entity, query].join('/')

  // API VIS
  const visCliques = ({ project }) => ['/api', 'vis', 'projects', project, 'cliques'].join('/')
  const visCliquesFile = ({ project, file }) => ['/api', 'vis', 'projects', project, 'files', file, 'cliques'].join('/')
  const visEntities = ({ project }) => ['/api', 'vis', 'projects', project, 'entities'].join('/')
  const visEntitiesFile = ({ project, file }) => ['/api', 'vis', 'projects', project, 'files', file, 'entities'].join('/')
  const visEntitiesUnbound = ({ project }) => ['/api', 'vis', 'projects', project, 'entities', 'unboundedEntities'].join('/')
  const visEntitiesUnboundFile = ({ project, file }) => ['/api', 'vis', 'projects', project, 'files', file, 'entities', 'unboundedEntities'].join('/')

  const visProjects = () => ['/api', 'vis', 'projects'].join('/')
  const visHistory = ({ project }) => ['/api', 'vis', 'projects', project, 'history'].join('/')
  const visFiles = ({ project }) => ['/api', 'vis', 'projects', project, 'files'].join('/')
  const visFile = ({ project, file }) => ['/api', 'vis', 'projects', project, 'files', file].join('/')
  const visFileMeta = ({ project, file }) => ['/api', 'vis', 'projects', project, 'files', file, 'meta'].join('/')
  const visAnnotations = ({ project, file }) => ['/api', 'vis', 'projects', project, 'files', file, 'certainties'].join('/')
  const visContext = ({ project, query }) => ['/api', 'vis', 'projects', project, 'context', query].join('/')

  function _init (args) {
    const obj = {
      // PROJECT SETTINGS
      getContributors: (options, params, data) => _createCall('GET', _createUrl(contributorsUrl, options, params), data),
      getSettings: (options, params, data) => _createCall('GET', _createUrl(settingsUrl, options, params), data),
      getProjectVersions: (options, params, data) => _createCall('GET', _createUrl(projectVersionsUrl, options, params), data),

      // VIS DASHBOARD
      updateDashboard: (options, params, data) => _createCall('POST', _createUrl(updateUrl, options, params), data),

      // STATS
      getStats: (options, params, data) => _createCall('GET', _createUrl(statsUrl, options, params), data),

      // CLOSE READING
      getFileHistory: (options, params, data) => _createCall('GET', _createUrl(closeHistory, options, params), data),
      fuzzysearch: (options, params, data) => _createCall('GET', _createUrl(fuzzysearch, options, params), data),

      // API VIS
      getCliques: (options, params, data) => _createCall('GET', _createUrl(visCliques, options, params), data),
      getFileCliques: (options, params, data) => _createCall('GET', _createUrl(visCliquesFile, options, params), data),
      getEntities: (options, params, data) => _createCall('GET', _createUrl(visEntities, options, params), data),
      getFileEntities: (options, params, data) => _createCall('GET', _createUrl(visEntitiesFile, options, params), data),
      getUnboundEntities: (options, params, data) => _createCall('GET', _createUrl(visEntitiesUnbound, options, params), data),
      getFileUnboundEntities: (options, params, data) => _createCall('GET', _createUrl(visEntitiesUnboundFile, options, params), data),

      getProjects: (options, params, data) => _createCall('GET', _createUrl(visProjects, options, params), data),
      getHistory: (options, params, data) => _createCall('GET', _createUrl(visHistory, options, params), data),
      getFiles: (options, params, data) => _createCall('GET', _createUrl(visFiles, options, params), data),
      getFile: (options, params, data) => _createCall('GET', _createUrl(visFile, options, params), data),
      getFileMeta: (options, params, data) => _createCall('GET', _createUrl(visFileMeta, options, params), data),
      getAnnotations: (options, params, data) => _createCall('GET', _createUrl(visAnnotations, options, params), data),
      getSearchContext: (options, params, data) => _createCall('GET', _createUrl(visContext, options, params), data)
    }

    return obj
  }

  function _createUrl (resource, options, params) {
    const paramsString = Object.entries(params).map(([key, value]) => `?${key}=${value}`).join('')
    const url = baseUrl + resource(options) + paramsString + '/'
    return url
  }

  function _createCall (method, url, data = {}) {
    function getCookie (name) {
      let cookieValue = null
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim()
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
          }
        }
      }
      return cookieValue
    }

    const csrftoken = getCookie('csrftoken')

    return new Promise(function (resolve, reject) {
      function csrfSafeMethod (method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method))
      }

      $.ajaxSetup({
        beforeSend: function (xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken)
          }
        }
      })

      try {
        $.ajax({
          url: url,
          type: method, // type is any HTTP method
          data: data, // Data as js object
          statusCode: {
            304: function () { resolve({ success: false, content: 'Not Modified.' }) },
            202: function () { resolve({ success: false, content: 'Request Accepted But Not Completed.' }) },
            200: function (a) { resolve({ success: true, content: a }) }
          },
          error: function (a) { resolve({ success: false, content: a }) }
        })
      } catch (error) {
        resolve({ success: false, content: null })
      }
    })
  }

  return _init(args)
}

export default AjaxCalls
