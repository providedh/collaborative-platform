export default function getOnEventCallback (dataClient, dimension, data) {
  if (!data) { return null }

  return ({ source, target }) => {
    if (isValidFilterEvent(target, source, dimension) === true) {
      const label = target.data[0]

      if (isDimensionFiltered(dataClient, dimension)) {
        handleFilteredDimension(dataClient, dimension, label, data)
      } else {
        handleUnfilteredDimension(dataClient, dimension, label)
      }
    } else if (isValidFocusEvent(target, source, dimension)) {
      focusDocument(dataClient, dimension, target.data)
    }
  }
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
    dataClient.unfilter(dimension)
  } else {
    filterItems.splice(filterItems.indexOf(label), 1)

    if (dimension === 'certaintyCategory') {
      dataClient.filter(dimension, x => x && filterItems.includes(x.sort().join()))
    } else {
      dataClient.filter(dimension, x => filterItems.includes(x))
    }
  }
}

function addToFilter (dataClient, dimension, filterItems, label) {
  filterItems.push(label)

  if (dimension === 'certaintyCategory') {
    dataClient.filter(dimension, x => x && filterItems.includes(x.sort().join()))
  } else {
    dataClient.filter(dimension, x => filterItems.includes(x))
  }
}

function handleFilteredDimension (dataClient, dimension, label, data) {
  const filter = dataClient.getFilter(dimension)
  const items = dimension === 'certaintyCategory'
    ? [...data.keys()].map(x => [x])
    : [...data.keys()]
  const filterItems = dimension === 'certaintyCategory'
    ? items.filter(filter.filter).map(x => x.sort().join())
    : items.filter(filter.filter)

  if (filterItems.includes(label)) {
    removeFromFilter(dataClient, dimension, filterItems, label)
  } else {
    addToFilter(dataClient, dimension, filterItems, label)
  }
}

function handleUnfilteredDimension (dataClient, dimension, label) {
  if (dimension === 'certaintyCategory') {
    dataClient.filter(dimension, x => x && x.sort().join() === label)
  } else {
    dataClient.filter(dimension, x => x === label)
  }
}
