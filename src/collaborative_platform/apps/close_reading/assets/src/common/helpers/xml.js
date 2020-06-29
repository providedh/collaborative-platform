const spacer = 'xxxx'

export default {
  spacer,
  originalId: id => id.slice(spacer.length),
  replacedId: xmlid => spacer + xmlid,
  replaceXmlid: s => s.replace(/xml:id="/gm, 'id="' + spacer),
  getSelfClosedTags: text => text.match(/<[^>]+\/>/gm) || [],
  expandEmptyTag: tag => {
      const name = tag.match(/[^ ,<,/,>]+/gm)[0]
      const opening = tag.replace('/>','>')
      const closing = '</'+name+'>'

      return opening + closing
  },
  getBodyContent: content => /<body[^>]*>(?<content>(.|[\n\r])*)<\/body>/im.exec(content)?.groups?.content,
  getBodyTagLength: content => /^(?<tag><body[^>]*>)/.exec(content).groups.tag.length
}

// getBodyContent: content => /^<body[^>]*>(?<content>.*)<\/body>$/.exec(content)?.groups?.content,