import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

import { ParentSize } from '@vx/responsive'

import css from 'grid_style_layout' // eslint-disable-line no-unused-vars
import css_ from 'grid_style_resizable' // eslint-disable-line no-unused-vars
import GridLayout from 'react-grid-layout'

import styles from './style.module.css'
import './style.css'

import VisFrame from '../VisFrame'
import Views from '../../views'

const getDefPlacement = (idx, id) => ({
  i: id,
  x: 0,
  y: 0,
  w: 4,
  h: 4,
  minW: 4,
  minH: 4,
  isDraggable: true,
  isResizable: true
})

function useLayout (defLayout, views, liftState) {
  const [layout, setLayout] = useState(defLayout)

  const changeLayout = newLayout => {
    setLayout(newLayout)
    if (liftState !== null) { liftState({ layout: newLayout }) }
  }

  useEffect(() => {
    if (layout.length < views.length) {
      // console.log(layout, views)
      const newLayout = [...layout]
      for (let i = newLayout.length; i < views.length; i++) {
        newLayout.push(getDefPlacement(i, views[i].id))
      }
      // console.log(newLayout)
      setLayout(newLayout)
      if (liftState !== null) { liftState({ layout: newLayout }) }
    }
  }, [views])

  return [layout, changeLayout]
}

export default function Workspace ({ focused, onFocus, onClose, defLayout = [], liftState = null, views }) {
  const [layout, setLayout] = useLayout(defLayout, views, liftState)

  const viewmap = views.map((view, i) => (
    <div key={views[i].id}>
      <VisFrame index={i} focused={focused === i} onViewClose={onClose} onViewFocus={onFocus}>
        { React.createElement(Views[view.type], { ...view.config, layout: layout[i] }) }
      </VisFrame>
    </div>
  ))

  return (
    <div className={styles.workspace}>
      <ParentSize>
        {parent =>
          <GridLayout
            layout={layout}
            onLayoutChange={setLayout}
            width={parent.width}
            draggableCancel="input,textarea,img,svg,canvas"
            rowHeight={90}
            cols={10}
            className="layout"
            compactType={null}>
            {viewmap}
          </GridLayout>
        }
      </ParentSize>
    </div>
  )
}

Workspace.propTypes = {
  focused: PropTypes.number,
  onFocus: PropTypes.func,
  onClose: PropTypes.func,
  defLayout: PropTypes.array,
  liftState: PropTypes.func,
  views: PropTypes.array
}
