export default function (container, doc, settings) {
  const docEntities = settings.entities.map(e => doc.getElementsByTagName(e.name))
  const containerEntities = settings.entities.map(e => container.getElementsByTagName(e.name))
  const containerEntitiesFlattened = containerEntities.reduce((ac, dc) => [...ac, ...dc], [])
  const containerObjectNames = [...container.getElementsByTagName('objectname')]
  const id2entity = Object.fromEntries(
    containerEntitiesFlattened
      .filter(x => Object.hasOwnProperty.call(x.attributes, 'xml:id'))
      .map(x => [x.attributes['xml:id'].value, x])
  )
  const name2style = Object.fromEntries(
    settings.entities
      .map(e => [e.name, e])
  )

  containerEntitiesFlattened.forEach(e => {
    const entityName = (Object.hasOwnProperty.call(e.attributes, 'type') &&
    Object.hasOwnProperty.call(name2style, e.attributes.type.value))
      ? e.attributes.type.value
      : e.tagName.toLowerCase()

    applyStyle(e, name2style[entityName])
  })

  containerObjectNames.forEach(e => {
    if (!Object.hasOwnProperty.call(e.attributes, 'ref')) { return }

    const ref = e.attributes.ref.value.slice(1) // the ref value is preceeded with an # character
    if (!Object.hasOwnProperty.call(id2entity, ref)) { return }

    const target = id2entity[ref]
    const entityName = (Object.hasOwnProperty.call(target.attributes, 'type') &&
    Object.hasOwnProperty.call(name2style, target.attributes.type.value))
      ? target.attributes.type.value
      : target.tagName.toLowerCase()

    applyStyle(e, name2style[entityName])
  })
}

function applyStyle (node, style) {
  const icon = `"${style.icon}"`
  node.style.setProperty('border-bottom', 'solid 2px ' + style.color)
  node.style.setProperty('position', 'relative')
  // node.style.setProperty('display', 'inline-block');
  node.style.setProperty('height', '2em')
  node.append($.parseHTML(`<i class="fa entityIcon" style="color:${style.color};" data-icon=${icon}></i>`)[0])
}
