export default function getOptions (form, context) {
  const documentNames = Object.keys(context.name2document)
  const documentIds = Object.keys(context.id2document)
  const defaultConfig = [
    { name: 'showEntities', type: 'toogle', value: true },
    { name: 'showCertainty', type: 'toogle', value: true },
    { name: 'syncWithViews', type: 'toogle', value: false },
    { name: 'documentId', type: 'selection', value: documentIds[0], params: { options: documentIds, labels: documentNames } }
  ]

  if (form == null) { return defaultConfig }

  const currentValues = Object.fromEntries(
    form.map(x => [x.name, x.value])
  )
  const { syncWithViews, showEntities, showCertainty } = currentValues

  const configOptions = [
    { name: 'showEntities', type: 'toogle', value: showEntities },
    { name: 'showCertainty', type: 'toogle', value: showCertainty },
    { name: 'syncWithViews', type: 'toogle', value: syncWithViews }
  ]

  if (syncWithViews === false) {
    const documentId = Object.hasOwnProperty.call(currentValues, 'documentId') ? currentValues.documentId : documentIds[0]
    configOptions.push({ name: 'documentId', type: 'selection', value: documentId, params: { options: documentIds, labels: documentNames } })
  }

  return configOptions
}
