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

  nameTags.forEach(tag => {
    const hasRef = Object.hasOwnProperty.call(tag.attributes, 'ref')
    const hasRefAdded = Object.hasOwnProperty.call(tag.attributes, 'refAdded')
    let ref = hasRef === true ? tag.attributes.ref.value.slice(1) : ''
    ref = hasRefAdded === true ? tag.attributes.refAdded.value.slice(1) : ref
    if ((!hasRef && !hasRefAdded) ||
        !Object.hasOwnProperty.call(entityMap, ref)) { return }

    const details = {}

    details.id = tag.attributes['xml:id'].value
    details.htmlId = replacedId(tag.attributes['xml:id'].value)
    details.target = ref
    details.type = entityMap[details.target].type
    details.saved = !(Object.hasOwnProperty.call(tag.attributes, 'saved') && tag.attributes?.saved?.value === 'false')
    details.deleted = (Object.hasOwnProperty.call(tag.attributes, 'deleted') && tag.attributes?.deleted?.value === 'true')
    details.properties = entityMap[details.target].properties
    details.annotations = annotations.filter(d => d.target.slice(1) === details.id || d.target.slice(1) === details.target)

    entityDetails.push(details)
  })

  unlistableTags.forEach(tag => {
    const tagRef = Object.hasOwnProperty.call(tag.attributes, 'refAdded')
      ? tag.attributes.refAdded.value.slice(1)
      : tag.attributes.ref.value.slice(1)
    const details = {}

    details.id = tag.attributes['xml:id'].value
    details.htmlId = replacedId(tag.attributes['xml:id'].value)
    details.target = tagRef
    details.type = tag.tagName
    details.saved = !(Object.hasOwnProperty.call(tag.attributes, 'saved') && tag.attributes.saved.value === 'false')
    details.deleted = (Object.hasOwnProperty.call(tag.attributes, 'deleted') && tag.attributes.deleted.value === 'true')
    details.annotations = annotations.filter(d => d.target.slice(1) === details.target)
    details.properties = []

    conf[tag.tagName].properties.forEach(property => {
      if (Object.hasOwnProperty.call(tag.attributes, property) === true) {
        details.properties.push({
          name: property,
          value: tag.attributes[property].value,
          saved: true,
          deleted: false
        })
      } else { // lacking, unsaved, modified or deleted
        const isPresent = Object.hasOwnProperty.call(tag.attributes, property + 'Added')
        const isDeleted = Object.hasOwnProperty.call(tag.attributes, property + 'Deleted')
        const p = {
          name: property,
          saved: false,
          deleted: false
        }

        if (isPresent === false && isDeleted === false) { return }

        if (isPresent === true && isDeleted === false) { // unsaved
          p.value = tag.attributes[property + 'Added'].value
        } else if (isPresent === true && isDeleted === true) { // modified
          p.value = tag.attributes[property + 'Added'].value

          if (tag.attributes[property + 'Added'].value === tag.attributes[property + 'Deleted'].value) {
            p.value = tag.attributes[property + 'Deleted'].value
            p.deleted = true
          }
        } else { // deleted
          p.value = tag.attributes[property + 'Deleted'].value
          p.deleted = true
        }

        details.properties.push(p)
      }
    })

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
