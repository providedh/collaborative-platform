import endpoints from './endpoints'
import { port } from './config.js'

/* Module for building full API call urls and returning JS Promises.
 *
 * */
export default (function (args) {
  const baseUrl = [window.location.protocol + '/', window.location.hostname + ':' + port].join('/')

  function _init (args) {
    const obj = {}
    Object.entries(endpoints).forEach(([endpointName, { method, builder }]) => {
      obj[endpointName] =
                (options, params, data) => _createCall(method, _createUrl(builder, options, params), data)
    })

    return obj
  }

  function _createUrl (resource, options, params) {
    const paramsString = Object.entries(params).map(([key, value]) => `?${key}=${value}`).join('')
    const url = baseUrl + resource(options) + paramsString
    return url
  }

  function _createCall (method, url, data = {}) {
    /* To use when injecting CSRF coockie for DJango login

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

      const csrftoken = getCookie('csrftoken');
    */

    const fetchBody = {
      method: method,
      mode: 'cors', // no-cors, *cors, same-origin
      cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
      credentials: 'same-origin', // include, *same-origin, omit
      headers: {
        'Content-Type': 'application/json'
      },
      redirect: 'follow',
      referrer: 'no-referrer' // no-referrer, *client
    }

    if (method === 'POST') {
      fetchBody.body = JSON.stringify(data) // body data type must match "Content-Type" header
    }

    return new Promise((resolve, reject) => {
      fetch(url, fetchBody)
        .then((response) => {
          response.json()
            .then((json) => resolve(json))
            .catch((err) => { reject(err) })
        })
        .catch((err) => { reject(err) })
    })
  }

  return _init(args)
})()
