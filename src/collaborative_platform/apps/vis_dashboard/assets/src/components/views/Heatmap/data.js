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
          accessor = d => [d['xml:id'], d.categories]
        break
        case SourceOption.entityProperties:
          accessor = d => [d.id, Object.keys(d.properties)]
        break
        case SourceOption.entityConcurrency:
          accessor = d => [d.type, d.filename]
        break
      }

      const preprocessed = preprocessData(data, accessor, entityType, source)
      const processed = processData(preprocessed) 
      setData(processed)
    })
  }, [source, entityType])

  return data
}

function preprocessData(data, accessor, entityType, source) {
  let preprocessed = null

  switch (source) {
    case SourceOption.uncertaintyCategories:
      preprocessed = {
        all: data.filtered.map(accessor),
        filtered: data.filtered.map(accessor)
      }
    break
    case SourceOption.entityProperties:
      preprocessed = {
        all: data.all.filter(d => d.type === entityType).map(accessor),
        filtered: data.filtered.filter(d => d.type === entityType).map(accessor)
      }
    break
    case SourceOption.entityConcurrency:
      const byFiles = {
        all: {},
        filtered: {}
      }

      data.filtered.forEach(d => {
        const [type, filename] = accessor(d)
        if (byFiles.filtered?.[filename] === undefined) {
          byFiles.filtered[filename] = new Set()
        }
        byFiles.filtered[filename].add(type)
      })

      data.all.forEach(d => {
        const [type, filename] = accessor(d)
        if (byFiles.all?.[filename] === undefined) {
          byFiles.all[filename] = new Set()
        }
        byFiles.all[filename].add(type)
      })


      preprocessed = {
        all: Object.entries(byFiles.all),
        filtered: Object.entries(byFiles.filtered)
      }
    break
  }

  return preprocessed
}

function processData(preprocessed) {
  function fillObject(object, items) {
    items.forEach(([item, categories]) => {
      [...categories].forEach(c => {
        if (object?.[c] === undefined) {
          object[c] = new Set()
        }
        object[c].add(item)
      })
    })
  }
  const data = { all: {}, filtered: {} }
  fillObject(data.all, preprocessed.all)
  fillObject(data.filtered, preprocessed.filtered)

  return data
}