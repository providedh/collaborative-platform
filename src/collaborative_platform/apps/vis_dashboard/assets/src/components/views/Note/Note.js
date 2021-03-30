import React, { useRef, useEffect } from 'react'
import PropTypes from 'prop-types'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

import styles from './style.module.css'
import getConfig from './config'

function useMarkdown (container, markdownContent) {
  useEffect(() => {
    if (container !== undefined) {
      const originalText = markdownContent.replace(/\\n/g, '\n')
      const markdownHtml = (new MarkdownIt()).render(originalText)
      const clean = DOMPurify.sanitize(markdownHtml)
      container.innerHTML = clean
    }
  }, [markdownContent, container])
}

export default function Note ({ note, layout, context }) {
  const containerRef = useRef()
  useMarkdown(containerRef.current, note)

  return (
    <div className={styles.container} ref={containerRef}>
    </div>
  )
}

Note.prototype.description = 'Add your findings and thoughts using Markdown notes.'

Note.prototype.getConfigOptions = getConfig

Note.propTypes = {
  layout: PropTypes.shape({
    w: PropTypes.number,
    h: PropTypes.number
  }),
  context: PropTypes.shape({
    taxonomy: PropTypes.object
  }),
  note: PropTypes.string
}
