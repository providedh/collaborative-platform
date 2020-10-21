import CSSstyles from './css.js'
import styleEntity from './entity_styles.js'
import styleEntityAnnotations from './certainty_styles.js'
import xml from 'common/helpers/xml.js'
import { Selection, SelectionType } from 'common/types'

export default function useContentRendering (node, documentContent, callbacks, context) {
  if (documentContent.length === 0) { return }
  const css = CSSstyles({ styleContainerId: 'dynamic-styling' })

  css.resetStyles()

  const xmlidReplaced = xml.replaceXmlid(documentContent)
  const bodyContent = xml.extractAndExpandTags(xmlidReplaced)(xmlidReplaced)

  const parser = new DOMParser()
  const xmlDoc = parser.parseFromString(bodyContent, 'text/xml')
  const body = xmlDoc.getElementsByTagName('body')[0]

  node.innerHTML = ''
  node.appendChild(body)
  // return 0
  styleEntities(context.entities, context.configuration, css)
  styleAnnotations(context.entities, context, css)
  setupEntityInteractions(context.entities, callbacks)
}

function styleEntities (entities, configuration, css) {
  entities.forEach(entity => {
    const styles = configuration.entities[entity.type]
    styleEntity(entity.htmlId.value, styles.color, styles.icon, css)
  })
}

function styleAnnotations (entities, context, css) {
  entities.forEach(entity => {
    if (entity.annotations.length === 0) { return }
    styleEntityAnnotations(entity.htmlId.value, entity.annotations, context, css)
  })
}

function setupEntityInteractions (entities, callbacks) {
  entities.forEach(entity => {
    const { onHover, onHoverOut, onClick } = callbacks
    const node = document.getElementById(entity.htmlId.value)

    node.addEventListener('mouseenter', event => {
      handleEntityEvent(entity, event, onHover, SelectionType.hover)
    })
    node.addEventListener('mouseout', event => {
      onHoverOut()
    })
    node.addEventListener('click', event => {
      event.preventDefault()
      handleEntityEvent(entity, event, onClick, SelectionType.click)
    })
  })
}

function handleEntityEvent (target, event, callback, type) {
  const boundingRect = event.target.getBoundingClientRect()
  // const parentBoundingRect = event.target.parentElement.getBoundingClientRect()
  // screenX absolute placement is harder to work with
  // const screenX = boundingRect.x + (boundingRect.width / 2)

  const screenY = boundingRect.y + window.scrollY + boundingRect.height - 15
  const selection = Selection(type, target, event.clientX, screenY)
  callback(selection)
}
