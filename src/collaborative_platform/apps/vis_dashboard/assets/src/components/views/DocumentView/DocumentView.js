import React, { useEffect, useState, useRef } from 'react'
import PropTypes from 'prop-types'

import { AjaxCalls } from '../../../helpers'
import { DataClient, useCleanup } from '../../../data'

import styles from './style.module.css'
import css from './style.css' // eslint-disable-line no-unused-vars
import getConfig from './config'
import styleEntities from './entityStyling'
import styleCertainty from './certaintyStyling'

const ajax = AjaxCalls()

function useData (dataClient, syncWithViews, documentId, id2Document) {
  const [data, setData] = useState({ id: '', name: '', html: '' })

  useEffect(() => {
    if (syncWithViews === true) {
      if (dataClient.getSubscriptions().includes('document')) { dataClient.unsubscribe('document') }

      dataClient.subscribe('document', ({ id, html }) => {
        if (id === null || html === null) { return }

        if (id !== '') {
          setData({ id, html: html.getElementsByTagName('body')[0].innerHTML, doc: html, name: id2Document[id].name })
        } else {
          setData({ id: '', html: '<i>Hover over documents in other views to see its contents here.</i>', doc: null, name: '' })
        }
      })
    } else {
      if (dataClient.getSubscriptions().includes('document')) { dataClient.unsubscribe('document') }

      ajax.getFile({ project: window.project, file: documentId }, {}, null).then(response => {
        if (response.success === true) {
          setData({
            id: documentId,
            name: id2Document[documentId].name,
            doc: response.content,
            html: response.content.getElementsByTagName('body')[0].innerHTML
          })
        }
      })
    }
  }, [syncWithViews, documentId])

  return data
}

function useRawData (dataClient, syncWithViews, documentId, id2Document) {
  const [data, setData] = useState({ id: '', name: '', html: '' })

  useEffect(() => {
    if (syncWithViews === true) {
      if (dataClient.getSubscriptions().includes('document')) { dataClient.unsubscribe('document') }

      dataClient.subscribe('document', ({ id, html }) => {
        if (id === null || html === null) { return }

        if (id !== '') {
          setData({ id, html: html, doc: html, name: id2Document[id].name })
        } else {
          setData({ id: '', html: 'Hover over documents in other views to see its contents here.', doc: null, name: '' })
        }
      })
    } else {
      if (dataClient.getSubscriptions().includes('document')) { dataClient.unsubscribe('document') }

      ajax.getFile({ project: window.project, file: documentId }, {}, null).then(response => {
        if (response.success === true) {
          setData({
            id: documentId,
            name: id2Document[documentId].name,
            doc: response.content,
            html: response.content
          })
        }
      })
    }
  }, [syncWithViews, documentId])

  return data
}

function useDocumentRendering (data, container, taxonomy) {
  useEffect(() => {
    if (container === undefined) { return }

    container.innerHTML = data.html
    styleEntities(container, data.doc, taxonomy)
    styleCertainty(container, data.doc, taxonomy)
  }, [data.id])
}

function useRawDocumentRendering (data, container, taxonomy) {
  useEffect(() => {
    if (container === undefined) { return }

    container.innerHTML = data.html
  }, [data.id])
}

export default function DocumentView ({ layout, syncWithViews, documentId, showEntities, showCertainty, context }) {
  const viewRef = useRef()

  const dataClient = useState(DataClient())[0]
  const data = useRawData(dataClient, syncWithViews, documentId, context.id2document)
  useRawDocumentRendering(data, viewRef.current, context.taxonomy)
  useCleanup(dataClient)

  return (
    <div className={styles.documentView}>
      <div className="bg-white d-flex justify-content-between justify-space-between p-2">
        <span className={styles.docName}>{data.name}</span>
        {data.id !== '' ? (
          <a className="btn btn-sm btn-outline-primary"
            target="blank"
            href={`/close_reading/project/${window.project}/file/${data.id}/`}>
          Open in annotator
          </a>) : ''}
      </div>
      <div ref={viewRef} className={styles.documentContainer + (showEntities ? ' ' : ' hideEntities ') + (showCertainty ? '' : 'hideCertainty')}>
      </div>
    </div>
  )
}

DocumentView.prototype.description = 'Encode frequencies using horizontal or vertical bars.'

DocumentView.prototype.getConfigOptions = getConfig

DocumentView.propTypes = {
  layout: PropTypes.shape({
    w: PropTypes.number,
    h: PropTypes.number
  }),
  context: PropTypes.object,
  syncWithViews: PropTypes.bool,
  documentId: PropTypes.string,
  showEntities: PropTypes.bool,
  showCertainty: PropTypes.bool
}
