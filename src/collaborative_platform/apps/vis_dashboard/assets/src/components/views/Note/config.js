const defaultConfig = [
  { name: 'note', type: 'textArea', value: '', params: { placeholder: 'Write your note' } }
]

export default function getOptions (form) {
  if (form == null) { return defaultConfig }

  const currentValues = {}
  form.forEach(x => { currentValues[x.name] = x.value })

  const { note } = currentValues

  const configOptions = [
    { name: 'note', type: 'textArea', value: note, params: { placeholder: 'Write your note' } }
  ]

  return configOptions
}
