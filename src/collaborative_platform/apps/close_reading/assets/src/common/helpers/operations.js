export function discardOperations(operations, operationId) {
	const o = operations.filter(o => o.id === operationId)?.[0]
	if (o === undefined) { raise('Tried to discard a non-existent operation') }

  const dependent = operations.filter(o => o.dependencies.includes(operationId))
  if (dependent.length === 0) { return operationId }
  return new Set([operationId, ...o.dependencies.map(discardOperations)])
}

export function saveOperations(operations, operationId) {
	const o = operations.filter(o => o.id === operationId)?.[0]
	if (o === undefined) { raise('Tried to save a non-existent operation') }

	if (o.dependencies.length === 0) { return operationId }

	return new Set([operationId, ...o.dependencies.map(saveOperations)])
}