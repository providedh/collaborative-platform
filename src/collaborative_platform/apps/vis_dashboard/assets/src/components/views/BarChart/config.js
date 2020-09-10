const BarChartDirection = {
  horizontal: 'Horizontal',
  vertical: 'Vertical'
}

const BarChartDimension = {
  entitiesPerDoc: 'Number of entities per document',
  entitiesPerType: 'Number of entities per type',
  annotationsPerDoc: 'Number of annotations per document',
  annotationsPerCategory: 'Number of annotations per category',
  annotationsPerAuthor: 'Number of annotations per author',
  commonAttributeValues: "Entity attributes",
  annotationAttributes: 'Most common annotated attribute values',
  annotationLocus: 'Type of annotation'
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

export default function (entities){
  return function getOptions (form) {
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

    if (dimension === 'commonAttributeValues') {
      console.log(currentValues)
      const entityNames = entities.map(x => x.name)
      configOptions.push({
        name: 'entityType',
        type: 'selection',
        value: currentValues?.entityType === undefined ? entityNames[0] : currentValues.entityType,
        params: { options: entityNames, labels: entityNames }
      })
    }

    return configOptions
  }
}
