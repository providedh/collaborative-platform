/* Module: WebSocket
 * Module implementing the websocket functionallity needed for
 * retrieving and annotating TEI files.
 *
 * Callbacks can be added for each of the events that the websocket
 * produces : onopen, onload, onreload, onsend
 * */

import validateContent from './content_response_schema'
import validateUsers from './users_response_schema'

export default function AnnotatorWebSocket (projectId, fileId) {
  let content = ''

  let socket = null
  let firstEntry = true

  const callbacks = {
    onopen: [],
    onload: [],
    onreload: [],
    onsend: []
  }

  function _addCallback (event, callback) {
    if (['onopen', 'onload', 'onreload', 'onsend'].includes(event) &&
                typeof (callback) === 'function') {
      callbacks[event].push(callback)
    }
  }

  function _createWebSocket () {
    const wsPrefix = (window.location.protocol === 'https:') ? 'wss:' : 'ws:'

    socket = new WebSocket(wsPrefix + window.location.host + '/ws/close_reading/' + projectId + '_' + fileId + '/')

    if (socket.readyState === WebSocket.OPEN) {
      socket.onopen()
    }

    socket.onopen = function open () {
      console.info('WebSockets connection created.')

      // Run any callbacks if any
      for (const callback of callbacks.onopen) { callback() }
    }

    socket.onmessage = function message (event) {
      const content = JSON.parse(event.data)
      let ok = true
      const validContentUpdate = validateContent(content)
      const validUsersUpdate = validateUsers(content)

      if (validContentUpdate.valid === true) {
        content.type = 'content';
        if (content.status !== 200) { ok = false }

      } else if (validUsersUpdate.valid === true) {
        content.type = 'users';

      } else {
        console.info('ws::invalid::', content)
        ok = false
      }

      if (firstEntry === true) { firstEntry = false }
      // Run any callbacks if any, with the contents retrieved
      const f = firstEntry === true ? callbacks.onload : callbacks.onreload
      f.forEach(callback => callback({...content, ok}))
    }

    setInterval(function () {
      socket.send(JSON.stringify('heartbeat'))
    }, 30000)
  }

  function _send (json) {
    socket.send(json)

    // Run any callbacks if any
    for (const callback of callbacks.onsend) { callback() }
  };

  return {
    version: 1,
    send: _send,
    addCallback: _addCallback,
    connect: _createWebSocket
  }
}
