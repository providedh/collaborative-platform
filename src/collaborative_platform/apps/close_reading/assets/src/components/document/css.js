/* Module: CSSstyles
 * Utility methods for retrieving the color scheme
 * or calculating the color for a specific annotation
 *
 * */

export default function CSSstyles (args) {
  const self = {}
  let styleContainerId = null

  function _init (args) {
    if (!Object.hasOwnProperty.call(args, 'styleContainerId')) { return null }

    styleContainerId = args.styleContainerId

    if (document.getElementById(styleContainerId) === null) {
      const head = document.getElementsByTagName('head')[0]
      const styleContainer = _createStyleContainer(styleContainerId)
      head.appendChild(styleContainer)
    }

    self.addRule = _addRule
    self.addBeforeRule = _addBeforeRule
    self.addAfterRule = _addAfterRule
    self.addRuleForId = (id, rule) => _addRule('#' + id, rule)
    self.addBeforeRuleForId = (id, rule) => _addBeforeRule('#' + id, rule)
    self.addAfterRuleForId = (id, rule) => _addAfterRule('#' + id, rule)
    self.resetStyles = _resetStyles
    self.createLinearGradient = _createLinearGradient
    self.addCode = _addCode

    return self
  }

  function _addCode (code) {
    document.getElementById(styleContainerId).innerHTML += code
  }

  function _addRule (selector, rule) {
    document.getElementById(styleContainerId).innerHTML += `${selector}{${rule}}`
  }

  function _addBeforeRule (selector, rule) {
    document.getElementById(styleContainerId).innerHTML += `${selector}::before{${rule}}`
  }

  function _addAfterRule (selector, rule) {
    document.getElementById(styleContainerId).innerHTML += `${selector}::after{${rule}}`
  }

  function _resetStyles () {
    document.getElementById(styleContainerId).innerHTML = ''
  }

  function _createLinearGradient (gradStops, orientation = 0) {
    const gradStopsJoined = gradStops.join(', ')
    const grad = `
        background: -moz-linear-gradient(left, ${gradStopsJoined});
        background: -webkit-gradient(left top, ${gradStopsJoined});
        background: -webkit-linear-gradient(left, ${gradStopsJoined});
        background: -o-linear-gradient(left, ${gradStopsJoined});
        background: -ms-linear-gradient(left, ${gradStopsJoined});
        background: linear-gradient(to right, ${gradStopsJoined});
      `

    return grad
  }

  function _createStyleContainer (id) {
    const tagHtml = document.createElement('style')
    tagHtml.setAttribute('type', 'text/css')
    tagHtml.id = id
    return tagHtml
  }

  return _init(args)
}
