import React, {useRef, useEffect} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars

function useContent(container, url, entity) {
  useEffect(() => {
    fetch(url)
    .then(r => r.json())
    .then(json => {
      if (json?.data !== undefined && container !== undefined) {
        const doc = $.parseXML(json.data)
        const body =
          doc.getElementsByTagName('body')[0].innerHTML
        container.innerHTML = body
        highlightTargets(container, entity)
      }
    })
    .catch(err => console.error(err))
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

  return (
    <div ref={preview} className={styles.targetPreview}>
      
    </div>
  )
}

TargetPreview.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
