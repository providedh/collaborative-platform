const PixelCorpusSortBy = {
  mostSelfContributedFirst: 'mostSelfContributedFirst',
  leastSelfContributedFirst: 'leastSelfContributedFirst',
  lastEditedFirst: 'lastEditedFirst',
  lastEditedLast: 'lastEditedLast',
  higherEntityCountFirst: 'higherEntityCountFirst',
  higherEntityCountLast: 'higherEntityCountLast'
}

const PixelCorpusColorBy = {
  locus: 'locus',
  authorship: 'resp',
  category: 'categories',
  certaintyLevel: 'cert',
  entity: 'target',
}

const PixelCorpusSource = { entities: 'entity', certainty: 'certainty' }

const defaultConfig = [
  {
    name: 'source',
    type: 'selection',
    value: Object.values(PixelCorpusSource)[0],
    params: {
      options: Object.values(PixelCorpusSource),
      labels: Object.keys(PixelCorpusSource)
    }
  },
  {
    name: 'sortDocumentsBy',
    type: 'selection',
    value: Object.values(PixelCorpusSortBy)[0],
    params: {
      options: Object.values(PixelCorpusSortBy)
    }
  },
  {
    name: 'colorBy',
    type: 'selection',
    value: 'type',
    params: {
      options: ['type']
    }
  }
]

export { PixelCorpusSortBy, PixelCorpusColorBy, PixelCorpusSource }

export default function getOptions (form) {
  if (form == null) { return defaultConfig }

  const currentValues = {}
  form.forEach(x => { currentValues[x.name] = x.value })

  const { sortDocumentsBy, colorBy, source } = currentValues

  const configOptions = [
    { name: 'source', type: 'selection', value: source, params: { options: Object.values(PixelCorpusSource), labels: Object.keys(PixelCorpusSource) } },
    { name: 'sortDocumentsBy', type: 'selection', value: sortDocumentsBy, params: { options: Object.values(PixelCorpusSortBy) } }
  ]

  if (source === PixelCorpusSource.entities) {
    configOptions.push(
      { name: 'colorBy', type: 'selection', value: 'type', params: { options: ['type'] } }
    )
  } else {
    const color = ['type', 'author'].includes(colorBy)  ? PixelCorpusColorBy.locus : colorBy
    configOptions.push(
      { name: 'colorBy', type: 'selection', value: color, params: { labels: Object.keys(PixelCorpusColorBy), options: Object.values(PixelCorpusColorBy) } }
    )
  }
  return configOptions
}
