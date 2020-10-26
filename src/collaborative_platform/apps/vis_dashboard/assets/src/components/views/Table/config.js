export const DataSource = { entity: 'entity', certainty: 'certainty' }

const defaultConfig = [
  {
    name: 'source',
    type: 'selection',
    value: Object.values(DataSource)[0],
    params: {
      options: Object.values(DataSource),
      labels: Object.keys(DataSource)
    }
  },
]

export default function getOptions (form) {
  if (form == null) { return defaultConfig }

  const currentValues = {}
  form.forEach(x => { currentValues[x.name] = x.value })

  const { source } = currentValues

  const configOptions = [
    { name: 'source', type: 'selection', value: source, params: { options: Object.values(DataSource), labels: Object.keys(DataSource) } },
  ]

  return configOptions
}
