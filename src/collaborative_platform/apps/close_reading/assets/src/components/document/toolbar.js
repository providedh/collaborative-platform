import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { WithAppContext } from 'common/context/app'
import certaintyColor from './color_transparency.js'
import styles from './toolbar.module.css'

export default function ToolbarContext (props) {
  return (
    <WithAppContext>
      <Toolbar {...props}/>
    </WithAppContext>
  )
}

export function Toolbar (props) {
  const [optionsDisplayed, setOptionsDisplayed] = useState(false)
  const [legendDisplayed, setLegendDisplayed] = useState(false)
  const {
    renderEntities,
    colorEntities,
    renderCertainty,
    colorCertainty
  } = props

  const { entities, taxonomy } = props.context.configuration

  const entityEntries = Object.entries(entities).map(x => (
    <div key={x[0]} className={styles.entity}>
      <span style={{ backgroundColor: x[1].color }}></span>
      {x[0]}
    </div>
  ))

  const annotationEntries = Object.entries(taxonomy).map(x => (
    <div key={x[0]} className={styles.entity}>
      <span style={{ backgroundColor: certaintyColor(x[0], 'very low', taxonomy) }}></span>
      <span style={{ backgroundColor: certaintyColor(x[0], 'low', taxonomy) }}></span>
      <span style={{ backgroundColor: certaintyColor(x[0], 'medium', taxonomy) }}></span>
      <span style={{ backgroundColor: certaintyColor(x[0], 'high', taxonomy) }}></span>
      <span style={{ backgroundColor: certaintyColor(x[0], 'very high', taxonomy) }}></span>
      {x[0]}
    </div>
  ))

  const legendCssClasses = [
    styles.legend,
    legendDisplayed === true ? '' : ' d-none',
    'mx-2',
    'p-2',
    'rounded'
  ]

  return <div>
    <div className={styles.toolbarContainer}>
      <div className={styles.toggleLegend} onClick={() => setLegendDisplayed(!legendDisplayed)}>
        Show legend
        <i className={legendDisplayed === true ? ' ml-2 fas fa-chevron-down' : ' ml-2 fas fa-chevron-right'}></i>
      </div>
      <div className={styles.options}>
        <div className={optionsDisplayed === false ? 'd-none' : ''}>
          <div className="custom-control custom-switch d-inline mr-2">
            <input className="custom-control-input"
              type="checkbox"
              id="render-entities"
              checked={renderEntities.value}
              onChange={() => renderEntities.set(!renderEntities.value)}/>
            <label className="custom-control-label" htmlFor="render-entities">Show entities</label>
          </div>
          <div className="custom-control custom-switch d-inline mr-2">
            <input className="custom-control-input"
              type="checkbox"
              id="color-entities"
              checked={colorEntities.value}
              onChange={() => colorEntities.set(!colorEntities.value)}/>
            <label className="custom-control-label" htmlFor="color-entities">Color entities</label>
          </div>
          <div className="custom-control custom-switch d-inline mr-2">
            <input className="custom-control-input"
              type="checkbox"
              id="render-annotations"
              checked={renderCertainty.value}
              onChange={() => renderCertainty.set(!renderCertainty.value)}/>
            <label className="custom-control-label" htmlFor="render-annotations">Show annotations</label>
          </div>
          <div className="custom-control custom-switch d-inline mr-2">
            <input className="custom-control-input"
              type="checkbox"
              id="color-annotations"
              checked={colorCertainty.value}
              onChange={() => colorCertainty.set(!colorCertainty.value)}/>
            <label className="custom-control-label" htmlFor="color-annotations">Color annotations</label>
          </div>
        </div>
        <div className={styles.optionsWide} onClick={() => setOptionsDisplayed(!optionsDisplayed)}>
          <i className={styles.hovered + (optionsDisplayed === true ? ' d-none' : ' fas fa-chevron-left')}></i>
          <i className="fas fa-cog"></i>
          <i className={optionsDisplayed === false ? 'd-none' : 'fas fa-chevron-right'}></i>
        </div>
        <div className={styles.optionsNarrow} onClick={() => setOptionsDisplayed(!optionsDisplayed)}>
          <i className={optionsDisplayed === false ? 'd-none' : 'fas fa-chevron-left'}></i>
          <i className="fas fa-cog"></i>
          <i className={styles.hovered + (optionsDisplayed === true ? ' d-none' : ' fas fa-chevron-right')}></i>
        </div>
      </div>
    </div>
    <div className={legendCssClasses.join(' ')}>
      <span>Entities</span>
      <hr className="mt-1 mb-2" />
      <div className={styles.legendContainer + ' mb-3'}>
        {entityEntries}
      </div>
      <span>Annotations</span>
      <hr className="mt-1 mb-2" />
      <div className={styles.legendContainer}>
        {annotationEntries}
      </div>
    </div>
  </div>
}

Toolbar.propTypes = {
  renderEntities: PropTypes.shape({
    value: PropTypes.bool,
    set: PropTypes.func
  }),
  colorEntities: PropTypes.shape({
    value: PropTypes.bool,
    set: PropTypes.func
  }),
  renderCertainty: PropTypes.shape({
    value: PropTypes.bool,
    set: PropTypes.func
  }),
  colorCertainty: PropTypes.shape({
    value: PropTypes.bool,
    set: PropTypes.func
  }),
  context: PropTypes.shape({
    user: PropTypes.string,
    authors: PropTypes.array,
    annotations: PropTypes.array,
    entities: PropTypes.object,
    configuration: PropTypes.object
  })
}
