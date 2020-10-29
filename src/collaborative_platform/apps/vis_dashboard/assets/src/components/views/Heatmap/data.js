import { useEffect, useState } from 'react'
import {SourceOption} from './config.js'

export default function useData (dataClient, source, entityType) {
  const [data, setData] = useState(null)

  useEffect(() => {
    const dataSource = source === SourceOption.uncertaintyCategories
      ? 'certainty'
      : 'entity';
    dataClient.clearSubscriptions()
    dataClient.subscribe(dataSource, data => {
      if (data === null || data.all.length === 0) { return 0 }

      let accessor = null
      switch (source) {
        case SourceOption.uncertaintyCategories:
          accessor = d => d.categories
        break
        case SourceOption.entityProperties:
          accessor = d => Object.keys(d.properties)
        break
        case SourceOption.entityConcurrency:
          accessor = d => [d.type, d.filename]
        break
      }

      const selected = source !== SourceOption.entityProperties
        ? data
        : {
          all: data.all.filter(d => d.type === entityType),
          filtered: data.filtered.filter(d => d.type === entityType)
        }

      const [concurrenceMatrix, maxOccurrences] = processData(selected, accessor) 
      setData([concurrenceMatrix, maxOccurrences])
    })
  }, [source, entityType])

  return data
}

function processData(data, accessor) {
  const processed = {
    all: data.filtered.map(accessor),
    filtered: data.filtered.map(accessor)
  }

  return [processed, Math.max(...processed.all.map(d => d.length))]
}