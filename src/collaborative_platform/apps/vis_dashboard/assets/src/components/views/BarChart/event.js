export default function getOnEventCallback (dataClient, dimension, data) {
  if (!data) { return null }

  return ({ source, target }) => {
    if (isValidFilterEvent(target, source, dimension) === true) {
      filterData(target, dataClient, dimension, data)
    } else if (isValidFocusEvent(target, source, dimension)) {
      focusDocument(dataClient, dimension, target.data)
    }
  }
}

function filterData(target, dataClient, dimension, data) {
  const label = target.data[0]
  let newFilter = isDimensionFiltered(dataClient, dimension) === true
    ? handleFilteredDimension(dataClient, dimension, label, data)
    : handleUnfilteredDimension(dataClient, dimension, label)


  if (newFilter === null) {
    dataClient.unfilter(dimension)
  } else {
    dataClient.filter(dimension, newFilter)
  }

  filterIds(dataClient, data, dimension, newFilter)
}

function filterIds(dataClient, data, dimension, newFilter) {
  if (newFilter === null) { 
    dataClient.unfilter('entityId')
    dataClient.unfilter(dimension)
    return
  }

  const entries = [...data]
    .filter(([key, value]) => newFilter(key))
    .reduce((ac, dc) => [...ac, ...dc[1]], [])

  const ids = Object.hasOwnProperty.call(entries[0], 'target')
    ? new Set(entries.map(d => d.target))
    : new Set(entries.map(d => d.id))
  dataClient.filter('entityId', d => ids.has(d))
}

function isValidFilterEvent (target, source, dimension) {
  const isValid = (target.data[0] !== undefined &&
        source === 'click' &&
        dimension !== undefined)

  return isValid
}

function isValidFocusEvent (target, source, dimension) {
  const isValid = (target.data[0] !== undefined &&
        source === 'hover' &&
        dimension === 'fileId')

  return isValid
}

function focusDocument (dataClient, dimension, [docId, count]) {
  dataClient.focusDocument(docId)
}

function isDimensionFiltered (dataClient, dimension) {
  return dataClient.getFilters().includes(dimension)
}

function removeFromFilter (dataClient, dimension, filterItems, label) {
  if (filterItems.length === 1) {
    return null
  }

  if (['categories', 'entityPropertyKeys'].includes(dimension)) {
    const categories = uniqueArrays(filterItems)
    const [idx, found] = indexOfArray(label, categories)
    if (!found) { return x => arrayContained(x, categories) }


    categories.splice(idx, 1)
    if (categories.length === 0) {return null}
    return x => arrayContained(x, categories)
  } else {
    filterItems.splice(filterItems.indexOf(label), 1)
    return x => filterItems.includes(x)
  }
}

function addToFilter (dataClient, dimension, filterItems, label) {
  filterItems.push(label)

  if (['categories', 'entityPropertyKeys'].includes(dimension)) {
    return x => arrayContained(x, filterItems)
  } else {
    return x => filterItems.includes(x)
  }
}

function handleFilteredDimension (dataClient, dimension, label, data) {
  const filter = dataClient.getFilter(dimension)
  const items = [...data.keys()]
  const filterItems = items.filter(filter.filter)

  if (filterItems.map(a => a?.join?.(',') || a).includes(label.join?.(',') || label)) {
    return removeFromFilter(dataClient, dimension, filterItems, label)
  } else {
    return addToFilter(dataClient, dimension, filterItems, label)
  }
}

function handleUnfilteredDimension (dataClient, dimension, label) {
  if (['categories', 'entityPropertyKeys'].includes(dimension)) {
    return x => arrayEquals(x, label)
  } else {
    return x => x === label
  }
}

const indexOfArray = (x, arr) => arr.reduce(([idx, found], item) => found === true ? [idx, found] : [idx + 1, arrayEquals(x, item)], [-1, false])
const arrayEquals = (a, b) => a.length === b.length && a.map(d => b.includes(d)).reduce((ac,dc) => ac && dc, true)
const arrayContained = (x, arr) => arr.reduce((included, item) => included || arrayEquals(item, x), false)
const uniqueArrays = arr => arr.reduce((ac, dc) => arrayContained(dc, ac) ? ac : [dc, ...ac],[])