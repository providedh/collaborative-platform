import * as d3 from 'd3'

export const dimOptions = {
  numAnnotations: 'Number of annotations',
  certLevel: 'Certainty level',
  numDocuments: 'Amount of documents mentioned'
}

const defaultConfig = [
  {
    name: 'dimension',
    type: 'selection',
    value: dimOptions.numAnnotations,
    params: {
      options: Object.keys(dimOptions),
      labels: Object.values(dimOptions),
    }
  },
]

export default function getOptions (form) {
  if (form == null) { return defaultConfig }

  const currentValues = {}
  form.forEach(x => { currentValues[x.name] = x.value })

  let { dimension } = currentValues

  const configOptions = [
    {
      name: 'dimension',
      type: 'selection',
      value: dimension,
      params: {
        options: Object.keys(dimOptions),
        labels: Object.values(dimOptions),
      }
    },
    
  ]

  return configOptions
}
