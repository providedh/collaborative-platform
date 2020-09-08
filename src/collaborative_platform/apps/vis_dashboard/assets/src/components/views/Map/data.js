import { useEffect, useState } from 'react'

export default function useData (dataClient, renderedItems) {
  const [data, setData] = useState({ all: [], filtered: [] })

  useEffect(() => {
    dataClient.clearSubscriptions()

    dataClient.subscribe(renderedItems, d => {
      if (d != null) {
        const newData = {
          all: d.all,
          filtered: d.filtered
        }

        setData(newData)
      }
    })
  }, [renderedItems])

  /*useEffect(() => {
    if (fetched != null) {
      const newData = {
        filters: dataClient.getFilters(),
        all: {
          tree: createTree(fetched.all, levelKeys),
          count: fetched.all.length
        },
        filtered: {
          tree: createTree(fetched.filtered, levelKeys),
          count: fetched.filtered.length
        }
      }

      setData(newData)
    }
  }, [])*/

  return data
}
