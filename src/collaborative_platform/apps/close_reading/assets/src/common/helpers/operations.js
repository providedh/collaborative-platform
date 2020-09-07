export function discardOperations(operations, operationId) {
	const o = operations.filter(o => o.id === operationId)?.[0]
	if (o === undefined) { raise('Tried to discard a non-existent operation') }

  const dependent = operations.filter(o => o.dependencies.includes(operationId))
  if (dependent.length === 0) { return new Set([operationId]) }

  const dependencies = dependent
    .map(id => discardOperations(operations, id))
    .reduce((ac, dc) => [...ac, ...dc], [])
  return new Set([operationId, ...dependencies])
}

export function saveOperations(operations, operationId) {
	const o = operations.filter(o => o.id === operationId)?.[0]
	if (o === undefined) { raise('Tried to save a non-existent operation') }

	if (o.dependencies.length === 0) { return new Set([operationId]) }

  const dependencies = o.dependencies
    .map(id => saveOperations(operations, id))
    .reduce((ac, dc) => [...ac, ...dc], [])
	return new Set([operationId, ...dependencies])
}