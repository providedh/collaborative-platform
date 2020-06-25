const spacer = 'xxxx'

export default {
  spacer,
  originalId: id => id.slice(spacer.length),
  replacedId: xmlid => spacer + xmlid,
  replaceXmlid: s => s.replace(/xml:id="/gm, 'id="' + spacer)
}
