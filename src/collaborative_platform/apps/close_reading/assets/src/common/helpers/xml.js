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
  getBodyTagLength
}
