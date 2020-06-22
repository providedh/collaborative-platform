import CSSstyles from './css.js'
import ColorScheme from './color_transparency.js'
import styleEntity from './entity_styles.js'
import styleEntityAnnotations from './certainty_styles.js'
import xml from './xml.js'
import { Selection, SelectionType } from '../../common/types/index.js'

export default function useContentRendering(node, documentContent, callbacks, context) {
  const css = CSSstyles({styleContainerId: 'dynamic-styling'})
  const cert = ColorScheme({configuration: context.configuration})

  css.resetStyles()

  node.innerHTML = xml.replaceXmlid(documentContent)
  styleEntities(context.entities, context.configuration, css)
  styleAnnotations(context.entities, context.annotations, context, css)
  setupHoverInteractions(context.entities, callbacks)
}

function styleEntities(entities, configuration, css) {
  Object.entries(entities).forEach(([type, entityList]) => {
    entityList.forEach(entity => {
      const styles = configuration.entities[type]
      const id = xml.replacedId(entity['xml:id'])
      styleEntity(id, styles.color, styles.icon, css)
    })
  })
}

function styleAnnotations(entities, annotations, context, css) {
  const entityIds = []
  Object.entries(entities).forEach(([type, entityList]) => {
    entityIds.push(...entityList.map(x => x['xml:id']))
  })

  const annotationsByTarget = {}
  annotations
    .filter(annotation => entityIds.includes(annotation.target.slice(1)))
    .forEach(annotation => {
      if (!Object.hasOwnProperty.call(annotationsByTarget, annotation.target)){
        annotationsByTarget[annotation.target] = []
      }
      annotationsByTarget[annotation.target].push(annotation)
    })

  Object.entries(annotationsByTarget).forEach(([target, annotations]) => {
    styleEntityAnnotations(target.slice(1), annotations, context, css)
  })
}

function setupHoverInteractions (entities, callbacks) {
  const {onHover, onHoverOut, onClick, onClickOut} = callbacks

  Object.entries(entities).forEach(([type, entityList]) => {
    entityList.forEach(entity => {
      const node = document.getElementById(xml.replacedId(entity['xml:id']))
      node.addEventListener('mouseenter', event => {
        handleEntityEvent (entity['xml:id'], event, onHover, SelectionType.hover)
      })
      node.addEventListener('mouseout', event => {
        onHoverOut()
      })
      node.addEventListener('click', event => {
        event.preventDefault()
        handleEntityEvent (entity['xml:id'], event, onClick, SelectionType.click)
      })
    })
  })
}

function handleEntityEvent (id, event, callback, type) {
  const boundingRect = event.target.getBoundingClientRect()
  const screenX = boundingRect.x + (boundingRect.width / 2)
  const screenY = boundingRect.top + boundingRect.height
  const selection = Selection(type, id, event.clientX, screenY)
  callback(selection)
}