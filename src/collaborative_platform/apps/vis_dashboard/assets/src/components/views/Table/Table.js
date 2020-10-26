import React, { useState, useRef, useEffect } from 'react'
import PropTypes from 'prop-types'

import { DataClient, useCleanup } from '../../../data'
import css from './style.css' // eslint-disable-line no-unused-vars
import styles from './style.module.css'
import getConfig, {DataSource} from './config'

function useData (dataClient, source) {
  const [data, setData] = useState({ all: [], filtered: [], source: source })

  useEffect(() => {
    dataClient.clearSubscriptions()
    dataClient.subscribe(source, data => {
      setData({ ...data, source })
    })
  }, [source])

  return data
}

function EntityEntry({entity, context}) {
  const properties = Object
    .entries(entity.properties)
    .map(p => `${p[0]}: ${p[1]}`, '')
    .join(', ')

  const conf = context.taxonomy.entities.filter(d => d.name === entity.type)[0]

  return <div className={styles.entity}>
    <span style={{color: conf.color}} className="mr-2">
      <i className="fas" data={conf.icon}></i> {entity.id}
    </span>
    <span>{properties}</span>
    <span>
      <a target="blank" href={`/close_reading/project/${context.project}/file/${entity.file_id}/`}>File: {entity.filename}</a>
    </span>
  </div>
}

function AnnotationEntry({annotation, projectId}) {
  const properties = Object
    .entries(annotation.properties)
    .map(p => `${p[0]}: ${p[1]}`, '')
    .join(', ')

  return <div>
    <span scope="row">{annotation.id}</span>
    <span>{annotation.type}</span>
    <span>{properties}</span>
    <span>
      <a href={`/close_reading/project/${projectId}/file/${entity.file_id}/`}>{entity.filename}</a>
    </span>
  </div>
}

export default function Table ({ layout, source, context }) {
  const [width, height] = layout !== undefined ? [layout.w, layout.h] : [4, 4]
  const [page, setPage] = useState(0)
  const maxItems = 20

  const dataClient = useState(DataClient())[0]
  useCleanup(dataClient)

  const data = useData(dataClient, source)
  const pages = Math.ceil(data.filtered.length / maxItems)

  useEffect(() => {
    setPage(0)
  }, [data])

  const entriesData = data.filtered.slice(page*maxItems, Math.min((page+1)*maxItems, data.filtered.length))
  const entries = source === DataSource.entity ? (
    entriesData.map(d => <EntityEntry key={d.id} context={context} entity={d}/>)
  ) : (
    entriesData.map(d => <AnnotationEntry key={d.id} context={context} annotation={d}/>)
  )

  return (
    <div className={styles.table}>
      <div className={styles.container}>
        {entries}
      </div>
      <div className="ml-3">
        Looking at {page * maxItems} - {page * maxItems + entries.length} out of {data.filtered.length} entries
        <br/>
        <button
          type="button"
          onClick={() => setPage(Math.max(page-1, 0))}
          className="btn btn-link pl-0">Previous page</button>
        <button
          type="button"
          onClick={() => setPage(Math.min(page+1, pages - 1))}
          className="btn btn-link">Next page</button>
      </div>
    </div>
  )
}

Table.prototype.description = 'Display certainty annotations and entity details in a readable form.'

Table.prototype.getConfigOptions = getConfig

Table.propTypes = {
  layout: PropTypes.shape({
    w: PropTypes.number,
    h: PropTypes.number
  }),
  context: PropTypes.shape({
    taxonomy: PropTypes.object
  }),
  source: PropTypes.string
}
