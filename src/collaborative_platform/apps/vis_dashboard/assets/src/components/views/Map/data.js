import { useEffect, useState } from 'react'

export default function useData (dataClient) {
  const [entities, setEntities] = useState({all: [], filtered: [], allNonValid: 0, filteredNonValid: 0})
  const [uncertainty, setUncertainty] = useState({all: [], filtered: []})

  const isPlace = d => d.type === 'place'
  const isValidPlace = d => (
    d.properties?.geo !== undefined &&
    d.properties.geo.split(' ').length === 2)

  useEffect(() => {
    dataClient.clearSubscriptions()

    dataClient.subscribe('entity', d => {
      if (d != null) {
        const all = d.all.filter(isPlace)
        const filtered = d.filtered.filter(isPlace)
        const newData = {all: all.filter(isValidPlace), filtered: filtered.filter(isValidPlace)}
        newData.allNonValid = all.length - newData.all.length
        newData.filteredNonValid = filtered.length - newData.filtered.length
        setEntities(newData)
      }
    })
    
    dataClient.subscribe('certainty', d => {
      if (d != null) {
        const newData = {
          all: d.all,
          filtered: d.filtered,
        }
        setUncertainty(newData)
      }
    })
  }, [])

  const entityIds = {
    all: entities.all.map(d => d.id),
    filtered: entities.filtered.map(d => d.id)
  }

  const annotations = {
    all: uncertainty.all.filter(d => entityIds.all.includes(d.target)),
    filtered: uncertainty.filtered.filter(d => entityIds.filtered.includes(d.target)),
  }

  return {entities, annotations}
}