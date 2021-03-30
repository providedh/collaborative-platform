import * as d3 from 'd3'

const attributes = {
  entity: {
    options: ['name', 'type', 'properties', 'filename', 'file_id'],
    labels: ['text', 'type', 'properties', 'documentName', 'id']
  },
  certainty: {
    options: ['resp', 'locus', 'file_id', 'categories', 'match', 'cert', 'degree'],
    labels: ['author', 'type', 'document', 'category', 'attribute', 'certainty', 'degree']
  }
}

const defaultConfig = [
  {
    name: 'source',
    type: 'selection',
    value: 'certainty',
    params: {
      options: [
        'entity',
        'certainty'
      ]
    }
  },
  {
    name: 'numberOfLevels',
    type: 'selection',
    value: '3',
    params: { options: d3.range(1, attributes.certainty.options.length).map(x => x + '') }
  },
  { name: 'level1', type: 'selection', value: 'file_id', params: attributes.certainty },
  { name: 'level2', type: 'selection', value: 'locus', params: attributes.certainty },
  { name: 'level3', type: 'selection', value: 'cert', params: attributes.certainty }
]

function createLevelsControls (numberOfLevels, prevLevels, source) {
  const availableOptions = [...attributes[source].options]
  const levelValues = d3.range(1, (+numberOfLevels) + 1)
    .map(i => {
      if (Object.hasOwnProperty.call(prevLevels, 'level' + i)) {
        if (attributes[source].options.includes(prevLevels['level' + i])) {
          availableOptions.splice(availableOptions.indexOf(prevLevels['level' + i]), 1)
          return prevLevels['level' + i]
        } else {
          return availableOptions.shift()
        }
      } else {
        return availableOptions.shift()
      }
    })
  const levels = levelValues.map((x, i) => (
    {
      name: 'level' + (i + 1),
      type: 'selection',
      value: x,
      params: attributes[source]
    })
  )

  return levels
}

export default function getOptions (form) {
  if (form == null) { return defaultConfig }

  const currentValues = {}
  form.forEach(x => { currentValues[x.name] = x.value })

  let { source, numberOfLevels, ...prevLevels } = currentValues

  numberOfLevels = Math.min(numberOfLevels, attributes[source].options.length - 1)
  const levels = createLevelsControls(numberOfLevels, prevLevels, source)

  const configOptions = [
    {
      name: 'source',
      type: 'selection',
      value: source,
      params: {
        options: [
          'entity',
          'certainty'
        ]
      }
    },
    {
      name: 'numberOfLevels',
      type: 'selection',
      value: numberOfLevels,
      params: { options: d3.range(1, attributes[source].options.length).map(x => x + '') }
    },
    ...levels
  ]

  return configOptions
}
