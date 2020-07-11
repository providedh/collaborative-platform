function proxied () {
  const _common = []
  let _specific = {}

  const isPrivate = (key) => key[0] === '_'
  function update (properties) { _specific = properties }

  const handler = {
    get (target, key) {
      if (isPrivate(key)) { throw new Error(`Attempted to access ${key}`) }
      if (key === 'update') { return update }

      if (!Object.hasOwnProperty.call(_specific, key)) {
        return { properties: _common }
      } else {
        const properties = new Set([..._common, ..._specific[key].properties])
        return { properties: [...properties] }
      }
    },
    set (target, key, value) {
      return false
    }
  }

  return new Proxy({}, handler)
}

export default proxied()
