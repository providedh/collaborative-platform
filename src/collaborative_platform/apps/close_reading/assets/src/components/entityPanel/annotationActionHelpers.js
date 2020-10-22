import {
  WebsocketRequest,
  WebsocketRequestType,
  ActionType,
  ActionTarget,
  ActionObject,
  AtomicActionBuilder,
  OperationStatus
} from 'common/types'

export function onDeleteClick (id, websocket) {
  const builder = AtomicActionBuilder(ActionTarget.certainty, ActionType.delete, ActionObject.certainty)
  const action = builder(id)
  const request = WebsocketRequest(WebsocketRequestType.modify, [action])
  websocket.send(request)
}

export function onDiscard (operations, id, websocket) {
  const relatedOperations = [...discardOperations(operations, id), ...saveOperations(operations, id)]
  const operationsToDiscard = [...new Set(relatedOperations)]
  const request = WebsocketRequest(WebsocketRequestType.discard, operationsToDiscard)
  websocket.send(request)

}

export function onSave (operations, id, websocket) {
  const operationsToSave = [...saveOperations(operations, id)]
  const request = WebsocketRequest(WebsocketRequestType.save, operationsToSave)
  websocket.send(request)
}

export function onCreate (id, values, websocket) {
  const { locus, ana, cert, assertedValue, desc, match } = values
  const builder = AtomicActionBuilder(ActionTarget.certainty, ActionType.add, ActionObject.certainty)

  let action = builder(id, locus, ana, cert, assertedValue, desc)
  if (locus === 'attribute') {
    action = builder(`${id}/${match}`, 'value', ana, cert, assertedValue, desc)
  }

  const request = WebsocketRequest(WebsocketRequestType.modify, [action])
  websocket.send(request)
}

export function onModify (id, oldValues, newValues, edit, websocket) {
  const builder = AtomicActionBuilder(ActionTarget.certainty, ActionType.modify, ActionObject.certainty)
  const actions = []
  Object.entries(oldValues).map(([key, value]) => {
    if (key === 'ana') {
      const categories = value
        .split(' ')
        .map(x => x.split('#')[1])
        .sort()
        .join(' ')

      if (categories !== newValues.ana.sort().join(' ')) {
        actions.push(builder(id, 'categories', newValues.ana))
      }
    } else {
      if (value !== newValues[key]) {
        actions.push(builder(id, key, newValues[key]))
      }
    }
  })
  // const action = builder(id, attributeName, attributeValue)
  const request = WebsocketRequest(WebsocketRequestType.modify, actions)
  websocket.send(request)
  edit(null)
}