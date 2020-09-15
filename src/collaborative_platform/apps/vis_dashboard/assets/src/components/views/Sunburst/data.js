import { useEffect, useState } from 'react'

export default function useData (dataClient, source, levels) {
  const levelKeys = Object.entries(levels).sort((x, y) => x[0] - y[0]).map(x => x[1])
  const [fetched, setFetched] = useState(null)
  const [data, setData] = useState({ data: null, count: 0 })


  useEffect(() => {
    dataClient.clearSubscriptions()

    dataClient.subscribe(source, d => {
      let processed = null

      if (d !== null) {
        processed = source === 'certainty' ? {
          all: d.all.map(({categories, ...rest}) => ({categories: categories.join(','), ...rest})),
          filtered: d.filtered.map(({categories, ...rest}) => ({categories: categories.join(','), ...rest}))
        } : {
          all: d.all.map(({properties, ...rest}) => ({properties: Object.keys(properties).join(','), ...rest})),
          filtered: d.filtered.map(({properties, ...rest}) => ({properties: Object.keys(properties).join(','), ...rest}))
        }
      }

      if (processed != null) {
        const newData = {
          filters: dataClient.getFilters(),
          all: {
            tree: createTree(processed.all, levelKeys),
            count: processed.all.length
          },
          filtered: {
            tree: createTree(processed.filtered, levelKeys),
            count: processed.filtered.length
          }
        }

        setFetched(processed)
        setData(newData)
      }
    })
  }, [source])

  useEffect(() => {
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
  }, [levelKeys.join('_')])

  return data
}

function getAttrAccessor (key) {
  if (key !== 'category') return entry => entry[key]
  else return entry => entry[key].join(', ')
}

function createTree (data, levelKeys) {
  const accessors = levelKeys.map(key => getAttrAccessor(key))
  const tree = { name: 'root', children: group(data, accessors) } // hierarchy

  return tree
}

function group (data, keys) {
  function regroup (values, i) {
    if (i >= keys.length) return values
    const groupsMap = new Map()
    const keyof = keys[i++]

    for (const value of values) {
      const key = keyof(value) + '' // the attribute's value
      const group = groupsMap.get(key)

      if (group) group.children.push(value)
      else groupsMap.set(key, { name: group, children: [value] })
    }

    for (const [name, group] of groupsMap) {
      groupsMap.set(name, { name, children: regroup(group.children, i) })
    }

    const groups = [...groupsMap.values()] // [{name, children}]
    return groups
  }

  return regroup(data, 0)
}
