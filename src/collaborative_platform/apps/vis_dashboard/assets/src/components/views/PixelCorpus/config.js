const PixelCorpusSortBy = {
  mostSelfContributedFirst: 'mostSelfContributedFirst',
  leastSelfContributedFirst: 'leastSelfContributedFirst',
  lastEditedFirst: 'lastEditedFirst',
  lastEditedLast: 'lastEditedLast',
  higherEntityCountFirst: 'higherEntityCountFirst',
  higherEntityCountLast: 'higherEntityCountLast'
}

const PixelCorpusColorBy = {
  type: 'type',
  category: 'category',
  certaintyLevel: 'certaintyLevel',
  categoryAndCertaintyLevel: 'categoryAndCertaintyLevel',
  authorship: 'authorship',
  entity: 'entity',
  locus: 'locus'
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
    value: Object.values(PixelCorpusColorBy)[0],
    params: {
      options: Object.values(PixelCorpusColorBy).slice(0, 1)
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
      { name: 'colorBy', type: 'selection', value: Object.values(PixelCorpusColorBy)[0], params: { options: Object.values(PixelCorpusColorBy).slice(0, 1) } }
    )
  } else {
    const color = colorBy === PixelCorpusColorBy.type ? PixelCorpusColorBy.category : colorBy
    configOptions.push(
      { name: 'colorBy', type: 'selection', value: color, params: { options: Object.values(PixelCorpusColorBy).slice(1) } }
    )
  }

  return configOptions
}
