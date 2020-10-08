import React, {useRef, useEffect} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars

function useContent(container, url) {
  useEffect(() => {
    fetch(url)
    .then(r => r.json())
    .then(json => {
      if (json?.data !== undefined && container !== undefined) {
        console.log({'text': json.data})
        const doc = $.parseXML(json.data)
        const body =
          doc.getElementsByTagName('body')[0].innerHTML
        container.innerHTML = body
      }
    })
    .catch(err => console.error(err))
  }, [url, container])
}

export default function TargetPreview ({entity, projectId, configuration}) {
  if (entity === null) {return ''}
  const preview = useRef()

  const fileURL = `/api/files/${entity.file_id}/`
  useContent(preview.current, fileURL)

  return (
    <div ref={preview} className={styles.targetPreview}>
      
    </div>
  )
}

TargetPreview.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
