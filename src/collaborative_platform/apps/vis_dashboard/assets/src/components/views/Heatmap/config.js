export const SourceOption = {
  uncertaintyCategories: 'Uncertainty categories',
  entityProperties: 'Entity properties',
  entityConcurrency: 'Entity concurrency'
}

const defaultConfig = [
  {
    name: 'source',
    type: 'selection',
    value: SourceOption.uncertaintyCategories,
    params: {
      options: [
        SourceOption.uncertaintyCategories,
        SourceOption.entityProperties,
        SourceOption.entityConcurrency
      ]
    }
  },
]

export default function getOptions (form, cfg) {
  if (form == null) { return defaultConfig }

  const currentValues = {}
  form.forEach(x => { currentValues[x.name] = x.value })

  let { source, entityType } = currentValues

  const configOptions = [
    {
      name: 'source',
      type: 'selection',
      value: source,
      params: {
        options: [
          SourceOption.uncertaintyCategories,
          SourceOption.entityProperties,
          SourceOption.entityConcurrency
        ]
      }
    },
  ]

  if (source === SourceOption.entityProperties) {
    const entities = cfg.taxonomy.entities.map(x => x.name)
    configOptions.push({
      name: 'entityType',
      type: 'selection',
      value: entities.includes(entityType) ? entityType : entities[0],
      params: {
        options: entities
      }
    })
  }

  return configOptions
}
