import { OperationStatus } from 'common/types'

const spacer = 'xxxx'

function originalId (id) {
  return id.slice(spacer.length)
}

function replacedId (xmlid) {
  return spacer + xmlid
}

function replaceXmlid (s) {
  return s.replace(/xml:id="/gm, 'id="' + spacer)
}

function getSelfClosedTags (text) {
  return text.match(/<[^>]+\/>/gm) || []
}

function expandEmptyTag (tag) {
  const name = tag.match(/[^ ,<,/,>]+/gm)[0]
  const opening = tag.replace('/>', '>')
  const closing = '</' + name + '>'

  return opening + closing
}

function extractAndExpandTags (original) {
  const selfClosedTags = getSelfClosedTags(original)

  return function (text) {
    let expanded = text
    for (const emptyTag of selfClosedTags) {
      const expandedTag = expandEmptyTag(emptyTag)
      expanded = expanded.replace(new RegExp(emptyTag, 'ig'), expandedTag)
    }

    return expanded
  }
}

function extractAndCollapseTags (original) {
  const selfClosedTags = getSelfClosedTags(original)

  return function (text) {
    let collapsed = text
    for (const emptyTag of selfClosedTags) {
      const expandedTag = expandEmptyTag(emptyTag)
      collapsed = collapsed.replace(new RegExp(expandedTag, 'ig'), emptyTag)
    }

    return collapsed
  }
}

function getBodyContent (content) {
  const r = /<body[^>]*>(?<content>(.|[\n\r])*)<\/body>/im
  return r.exec(content)?.groups?.content
}

function getBodyTagLength (content) {
  const r = /^(?<tag><body[^>]*>)/
  return r.exec(content).groups.tag.length
}

function processTagAttribute (attr, domNode) {
  const attrValue = domNode.attributes?.[attr]?.value
  const addedValue = domNode.attributes?.[attr + 'Added']?.value
  const deletedValue = domNode.attributes?.[attr + 'Deleted']?.value

  if (attrValue !== undefined && addedValue === undefined && deletedValue === undefined) {
    return { name: attr, value: attrValue, status: OperationStatus.saved }
  } else if (addedValue !== undefined && deletedValue === undefined) {
    return { name: attr, value: addedValue, status: OperationStatus.unsaved }
  } else if (addedValue !== undefined && deletedValue !== undefined) {
    if (addedValue === deletedValue) {
      return { name: attr, value: addedValue, status: OperationStatus.deleted }
    } else if (addedValue !== deletedValue) {
      return {
        value: addedValue,
        prev: deletedValue,
        status: OperationStatus.edited
      }
    }
  } else {
    return { name: attr, value: null, status: OperationStatus.null }
  }
}

function processListableAttribute (attr, attrList) {
  const filtered = attrList.filter(x => x.name === attr)

  if (filtered.length === 1) {
    if (filtered[0].saved === false) {
      return { name: attr, value: filtered[0].value, status: OperationStatus.unsaved }
    } else if (filtered[0].saved === true && filtered[0].deleted === false) {
      return { name: attr, value: filtered[0].value, status: OperationStatus.saved }
    } else if (filtered[0].saved === true && filtered[0].deleted === true) {
      return { name: attr, value: filtered[0].value, status: OperationStatus.deleted }
    }
  } else if (filtered.length === 2) {
    let [prev, current] = filtered
    if (prev.saved === false) {
      [prev, current] = [current, prev]
    }
    return { name: attr, value: current.value, prev: prev.value, status: OperationStatus.edited }
  } else {
    return { name: attr, value: null, status: OperationStatus.null }
  }
}

function processTag (domNode) {
  const commonAttributeNames = ['xml:id', 'ref']
  const commonAttributes = Object.fromEntries(
    commonAttributeNames.map(attr => [attr, processTagAttribute(attr, domNode)])
  )

  commonAttributes.htmlId = Object.assign({}, commonAttributes['xml:id'])
  if (commonAttributes.htmlId.status === OperationStatus.edited) {
    commonAttributes.htmlId.value = replacedId(commonAttributes['xml:id'].prev)
  } else {
    commonAttributes.htmlId.value = replacedId(commonAttributes['xml:id'].value)
  }

  const tag = {
    id: commonAttributes['xml:id'],
    htmlId: commonAttributes.htmlId,
    ref: commonAttributes.ref,
    saved: !(domNode.attributes?.saved?.value === 'false'),
    deleted: (domNode.attributes?.deleted?.value === 'true')
  }

  if (Object.values(commonAttributes).filter(x => x.value === null).length > 0) {return null}

  tag.ref.value = tag.ref.value.slice(1)
  return tag
}

function processAnnotations (annotations, targets) {
  const filtered = annotations.filter(x => targets.includes(x.target.slice(1)))
  const distinctIds = new Set(filtered.map(x => x['xml:id']))

  const processed = [...distinctIds].map(id => {
    const annotation = filtered.filter(x => id === x['xml:id'])

    // process the match property
    annotation.forEach(x => {
      if (![null, undefined, ''].includes(x.match) && x.match.startsWith('@')) {
        x.locus = 'attribute'
        x.match = x.match.slice(1)
      }
    })

    // set the status
    if (annotation.length === 1) {
      if (annotation[0].saved === false) {
        return { status: OperationStatus.unsaved, ...annotation[0] }
      } else if (annotation[0].saved === true && annotation[0].deleted === false) {
        return { status: OperationStatus.saved, ...annotation[0] }
      } else if (annotation[0].saved === true && annotation[0].deleted === true) {
        return { status: OperationStatus.deleted, ...annotation[0] }
      }
    } else if (annotation.length === 2) {
      let [current, prev] = annotation
      if (current.saved === true && current.deleted === true) {
        [current, prev] = [prev, current]
      }
      return {
        status: OperationStatus.edited,
        prev,
        ...current
      }
    }
  })

  return processed
}

function processEntitiesInDocument (raw, entities, annotations, conf) {
  const unlistableEntities = Object.keys(conf).filter(k => conf[k].listable === false)
  const entityMap = Object.fromEntries(entities.map(e => [e['xml:id'], e]))

  // Get DOM elements
  const parser = new DOMParser()
  const xmlDoc = parser.parseFromString(raw, 'text/xml')
  const body = xmlDoc.getElementsByTagName('body')[0]

  const unlistableTags = []
  unlistableEntities.forEach(e => unlistableTags.push(...body.getElementsByTagName(e)))
  const nameTags = [...body.getElementsByTagName('name')]

  // Get details
  const entityDetails = []

  nameTags
    .map(tag => [tag, processTag(tag)])
    .filter(([tag, details]) => details !== null)
    .forEach(([tag, details]) => {
      const targetId = details.ref.value
      if (entityMap?.[targetId] === undefined) { return }

      details.target = details.ref
      details.type = entityMap[targetId].type

      const propertyNames = new Set(entityMap[targetId].properties.map(x => x.name))
      details.properties = [...propertyNames]
        .map(attr => processListableAttribute(attr, entityMap[targetId].properties))
        .filter(attr => attr.status !== OperationStatus.null)

      details.annotations = processAnnotations(annotations, [details.id.value, targetId])

    entityDetails.push(details)
  })

  // Unlistable entities
  unlistableTags
    .map(tag => [tag, processTag(tag)])
    .filter(([tag, details]) => details !== null && details.id.value === details.ref.value)
    .forEach(([tag, details]) => {
      details.target = details.ref
      details.type = tag.tagName
      details.annotations = processAnnotations(annotations, [details.target.value])
      details.properties = conf[tag.tagName].properties
        .map(attr => processTagAttribute(attr, tag))
        .filter(attr => attr.status !== OperationStatus.null)

      entityDetails.push(details)
    })

  // Tags refferring to unlistable entities
  unlistableTags
    .map(tag => [tag, processTag(tag)])
    .filter(([tag, details]) => details !== null && details.id.value === details.ref.value)
    .forEach(([tag, details]) => {
      const referredList = entityDetails.filter(d => d.id.value === details.ref.value)
      if (referredList.length === 0) { console.err(tag.id.value+' refers to a non-existent entity'); return }

      const referred = referredList[0]
      details.target = details.ref
      details.type = tag.tagName
      details.annotations = referred.annotations
      details.properties = referred.properties

      entityDetails.push(details)
    })

  return entityDetails
}

export default {
  spacer,
  originalId,
  replacedId,
  replaceXmlid,
  getSelfClosedTags,
  expandEmptyTag,
  extractAndExpandTags,
  extractAndCollapseTags,
  getBodyContent,
  getBodyTagLength,
  processEntitiesInDocument
}
