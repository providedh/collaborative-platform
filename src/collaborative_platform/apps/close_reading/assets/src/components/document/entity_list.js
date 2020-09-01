import React from 'react'
import PropTypes from 'prop-types'

import styles from './document.module.css'

export default function PersonList(props) {
  if (props.entities.length === 0) { return '' }
  const attr4entity = e => e.properties.map(({name, value}) => `${name}:${value}`).join(', ')

  return(
    <div>
      <h6>
        {props.type[0].toUpperCase() + props.type.slice(1)}s
      </h6>
      <ul>
        {props.entities.map(e => 
          <li key={e.id.value}>
            <span className={styles.icon} style={{ color: props.conf.color }} dataicon={props.conf.icon}>
              <div dangerouslySetInnerHTML={{ __html: props.conf.icon }} />
            </span> {e.id.value} <i className="text-secondary">({attr4entity(e)})</i>
          </li>)}
      </ul>
    </div>
  )
}

PersonList.propTypes = {
  type: PropTypes.string,
  entities: PropTypes.array,
  conf: PropTypes.object
}