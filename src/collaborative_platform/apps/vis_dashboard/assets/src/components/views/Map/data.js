import { useEffect, useState } from 'react'

export default function useData (dataClient) {
  const [entities, setEntities] = useState({all: [], filtered: []})
  const [uncertainty, setUncertainty] = useState({all: [], filtered: []})

  useEffect(() => {
    dataClient.clearSubscriptions()

    dataClient.subscribe('entity', d => {
      if (d != null) {
        const newData = {
          all: d.all.filter(e => e.type === 'place'),
          filtered: d.filtered.filter(e => e.type === 'place'),
        }
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