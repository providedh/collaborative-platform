import React, { useState } from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'
import TabControl from '../TabControl'

export default function TabContainer ({ labels, children }) {
  const [active, setActive] = useState(0)

  function handleActiveChange (option) {
    // this.props.panelNames always contains option because
    // the options are created from this array
    setActive(labels.indexOf(option))
  }

  return <div className={styles.tabContainer}>
    <TabControl labels={labels} active={active} onChange={handleActiveChange}/>
    <div className={styles.tab}>{children[active]}</div>
  </div>
}

TabContainer.propTypes = {
  labels: PropTypes.array,
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node
  ])
}
