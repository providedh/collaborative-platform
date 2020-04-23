const BarChartDirection = {
  horizontal: 'Horizontal',
  vertical: 'Vertical'
}

const BarChartDimension = {
  entitiesPerDoc: 'Number of entities per document',
  entitiesPerType: 'Number of entities per type',
  commonEntities: 'Most annotated entities',
  annotationsPerDoc: 'Number of annotations per document',
  annotationsPerCategory: 'Number of annotations per category',
  annotationsPerAuthor: 'Number of annotations per author',
  commonAttributeValues: "Frequency for an attribute's values",
  annotationAttributes: 'Frequency for most common attribute values'
}

const defaultConfig = [
  {
    name: 'barDirection',
    type: 'selection',
    value: Object.values(BarChartDirection)[0],
    params: { options: Object.values(BarChartDirection) }
  },
  {
    name: 'dimension',
    type: 'selection',
    value: Object.keys(BarChartDimension)[0],
    params: { options: Object.keys(BarChartDimension), labels: Object.values(BarChartDimension) }
  }
]

export { BarChartDimension }
export { BarChartDirection }

export default function getOptions (form) {
  if (form == null) { return defaultConfig }

  const currentValues = {}
  form.forEach(x => { currentValues[x.name] = x.value })

  const { barDirection, dimension } = currentValues

  const configOptions = [
    {
      name: 'barDirection',
      type: 'selection',
      value: barDirection,
      params: { options: Object.values(BarChartDirection) }
    },
    {
      name: 'dimension',
      type: 'selection',
      value: dimension,
      params: { options: Object.keys(BarChartDimension), labels: Object.values(BarChartDimension) }
    }
  ]

  return configOptions
}
