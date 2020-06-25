import CSSstyles from './css.js'
import styleEntity from './entity_styles.js'
import styleEntityAnnotations from './certainty_styles.js'
import xml from './xml.js'
import { Selection, SelectionType } from '../../common/types'

export default function useContentRendering (node, documentContent, callbacks, context) {
  const css = CSSstyles({ styleContainerId: 'dynamic-styling' })

  css.resetStyles()

  node.innerHTML = xml.replaceXmlid(documentContent)
  // return 0
  styleEntities(context.entities, context.configuration, css)
  styleNames(context.entities, context.configuration, css)
  styleAnnotations(context.entities, context.annotations, context, css)
  setupEntityHoverInteractions(context.entities, callbacks)
  setupNameHoverInteractions(context.entities, callbacks)
}

function styleEntities (entities, configuration, css) {
  Object.entries(entities).forEach(([type, entityList]) => {
    entityList.forEach(entity => {
      const styles = configuration.entities[type]
      const id = xml.replacedId(entity.properties['xml:id'])
      styleEntity(id, styles.color, styles.icon, css)
    })
  })
}

function styleNames (entities, configuration, css) {
  Object.entries(entities).forEach(([type, entityList]) => {
    entityList.forEach(entity => {
      const styles = configuration.entities[type]

      Array.from(document.getElementsByTagName('name'))
        .filter(x => x.attributes?.['ref']?.value === ('#' + entity['xml:id']))
        .forEach(x => styleEntity(x.id, styles.color, styles.icon, css))
    })
  })
}

function styleAnnotations (entities, annotations, context, css) {
  const entityIds = []
  Object.entries(entities).forEach(([type, entityList]) => {
    entityIds.push(...entityList.map(x => x['xml:id']))
  })

  const annotationsByTarget = {}
  annotations
    .filter(annotation => entityIds.includes(annotation.target.slice(1)))
    .forEach(annotation => {
      if (!Object.hasOwnProperty.call(annotationsByTarget, annotation.target)) {
        annotationsByTarget[annotation.target] = []
      }
      annotationsByTarget[annotation.target].push(annotation)
    })

  Object.entries(annotationsByTarget).forEach(([target, annotations]) => {
    styleEntityAnnotations(target.slice(1), annotations, context, css)
  })
}

function setupEntityHoverInteractions (entities, callbacks) {
  Object.entries(entities).forEach(([type, entityList]) => {
    entityList.forEach(entity => {
      const id = xml.replacedId(entity['xml:id'])
      const node = document.getElementById(id)
      if (node !== undefined && node !== null) {
        setupNodeHoverInteractions(node, entity['xml:id'], callbacks)
      }
    })
  })
}

function setupNameHoverInteractions (entities, callbacks) {
  Object.entries(entities).forEach(([type, entityList]) => {
    entityList.forEach(entity => {
      Array.from(document.getElementsByTagName('name'))
        .filter(x => x.attributes?.['ref']?.value === ('#' + entity['xml:id']))
        .forEach(node => setupNodeHoverInteractions(node, entity['xml:id'], callbacks))
    })
  })
}

function setupNodeHoverInteractions (node, entityId, callbacks) {
  const { onHover, onHoverOut, onClick } = callbacks
  node.addEventListener('mouseenter', event => {
    handleEntityEvent(entityId, event, onHover, SelectionType.hover)
  })
  node.addEventListener('mouseout', event => {
    onHoverOut()
  })
  node.addEventListener('click', event => {
    event.preventDefault()
    handleEntityEvent(entityId, event, onClick, SelectionType.click)
  })
}

function handleEntityEvent (id, event, callback, type) {
  const boundingRect = event.target.getBoundingClientRect()

  // screenX absolute placement is harder to work with
  // const screenX = boundingRect.x + (boundingRect.width / 2)

  const screenY = boundingRect.top + boundingRect.height
  const selection = Selection(type, id, event.clientX, screenY)
  callback(selection)
}
