import React, {useRef, useEffect} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars

function renderUrlContent(container, url, entity) {
  fetch(url)
    .then(r => r.json())
    .then(json => {
      if (json?.data !== undefined && container !== undefined) {
        const doc = $.parseXML(json.data)
        const body =
          doc.getElementsByTagName('text')[0].innerHTML
        container.innerHTML = body
        if (container.innerText.length === 0) {
          container.innerHTML = '<i>This file does not have text content.</i>'
        }
        highlightTargets(container, entity)
      }
    })
    .catch(err => console.error(err))
}

function useContent(container, url, entity) {
  useEffect(() => {
    renderUrlContent(container, url, entity)
  }, [url, container])
}

function useHighlight(container, entity) {
  const target = '#' + entity['xml:id']
  useEffect(() => {
    highlightTargets(container, entity)
  }, [target])
}

function highlightTargets(container, entity) {
  const target = '#' + entity['xml:id']
  if (container === undefined) {return}
  Array.from(container.getElementsByTagName('name'))
    .map(x => {
      x.classList.remove(styles.highlighted)
      return x
    })
    .filter(x => x.attributes?.ref?.value === target)
    .forEach(x => x.classList.add(styles.highlighted))
}

export default function TargetPreview ({entity, projectId, configuration}) {
  if (entity === null) {return ''}
  const preview = useRef()

  const fileURL = `/api/files/${entity.file_id}/`
  useContent(preview.current, fileURL, entity)
  useHighlight(preview.current, entity)

  useEffect(() => renderUrlContent(preview.current, fileURL, entity), [])

  return (
    <div ref={preview} className={styles.targetPreview}>Getting file . . .</div>
  )
}

TargetPreview.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
