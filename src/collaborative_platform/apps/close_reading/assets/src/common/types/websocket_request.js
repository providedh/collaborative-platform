export const WebsocketRequestType = {
  modify: 'modify',
  discard: 'discard',
  save: 'save'
}

export function WebsocketRequest (type, payload) {
  const request = {
    method: type,
    payload: payload
  }

  return JSON.stringify(request)
}
