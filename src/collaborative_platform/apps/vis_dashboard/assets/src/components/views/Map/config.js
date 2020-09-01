import * as d3 from 'd3'

export const options = {
  certainty: 'Annotations',
  entity: 'Entities'
}

const defaultConfig = [
  {
    name: 'renderedItems',
    type: 'selection',
    value: 'certainty',
    params: {
      options: Object.keys(options),
      labels: Object.values(options),
    }
  },
]

export default function getOptions (form) {
  if (form == null) { return defaultConfig }

  const currentValues = {}
  form.forEach(x => { currentValues[x.name] = x.value })

  let { renderedItems } = currentValues

  const configOptions = [
    {
      name: 'renderedItems',
      type: 'selection',
      value: renderedItems,
      params: {
        options: Object.keys(options),
        labels: Object.values(options),
      }
    }    
  ]

  return configOptions
}
