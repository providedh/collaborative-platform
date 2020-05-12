export default function (container, doc, settings) {
  const annotations = [...doc.getElementsByTagName('certainty')].filter(
    x => Object.hasOwnProperty.call(x.attributes, 'ana') && x.attributes.ana.value !== '')
  const targets = getTargets(annotations)
  const id2annotations = Object.fromEntries(targets.map(e => [e, []]))
  const containerEntities = [...settings.entities, { name: 'objectname' }].map(e => container.getElementsByTagName(e.name))
  const containerEntitiesFlattened = containerEntities.reduce((ac, dc) => [...ac, ...dc], [])
  const id2entity = Object.fromEntries(
    containerEntitiesFlattened
      .filter(x => Object.hasOwnProperty.call(x.attributes, 'xml:id'))
      .map(x => [x.attributes['xml:id'].value, x])
  )

  annotations.forEach(annotation => {
    annotation.attributes.target.value
      .split(' ')
      .map(x => x.slice(1))
      .filter(x => x !== '')
      .forEach(t => id2annotations[t].push(annotation))
  })

  targets.forEach(target => {
    if (!Object.hasOwnProperty.call(id2entity, target)) {

    } else {
      applyStyle(id2entity[target], id2annotations[target], settings)
    }
  })
}

function applyStyle (node, annotations, settings) {
  const category2style = Object.fromEntries(settings.taxonomy.map(x => [x.name, x]))
  const gradStops = []
  const numberAnnotations = annotations.length
  const annotationSpacer = 10
  const percIncrement = (100 - ((numberAnnotations - 1) * annotationSpacer)) / annotations.length// author=='#'+currentUser?'#fff0':'#ffff';

  let curPercentage = percIncrement

  const firstCategory = annotations[0]
    .attributes.ana.value
    .split(' ')[0]
    .split('#')[1]

  let color = category2style[firstCategory].color
  let prevColor = color
  gradStops.push(`${color} 0%`)

  annotations.forEach((annotation, i) => {
    annotation.attributes.ana.value.split(' ').forEach(category => {
      color = category2style[category.split('#')[1]].color + 'ff'

      gradStops.push(`${prevColor} ${curPercentage}%`)
      gradStops.push(`${color} ${curPercentage}%`)
      curPercentage += percIncrement

      prevColor = color
    })

    if (i <= numberAnnotations - 2) {
      curPercentage -= percIncrement
      gradStops.push(`var(--light) ${curPercentage}%`)
      curPercentage += annotationSpacer
      prevColor = 'var(--light)'
    }
  })

  gradStops.push(`${prevColor} 100%`)

  node.style.setProperty('background', `linear-gradient(to right, ${gradStops.join(', ')})`)
}

function getTargets (annotations) {
  const targets = annotations.map(a => a.attributes.target.value)
  const splitted = targets.reduce((ac, dc) => [...ac, ...dc.split(' ')], [])
  const trimmed = splitted.map(x => x.slice(1))
  const unique = [...(new Set(trimmed)).values()]
  return unique.filter(x => x !== '')
}
