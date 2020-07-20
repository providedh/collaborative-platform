/* Module: WebSocket
 * Module implementing the websocket functionallity needed for
 * retrieving and annotating TEI files.
 *
 * Callbacks can be added for each of the events that the websocket
 * produces : onopen, onload, onreload, onsend
 * */

import response from './mockup_data.js'

export default function AnnotatorWebSocket (projectId, fileId) {
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
    callbacks.onload.forEach(callback => callback(response))
  }

  function _send (json) {

  };

  return {
    version: 1,
    send: _send,
    addCallback: _addCallback,
    connect: _createWebSocket
  }
}
