import React, { useState } from 'react'
import PropTypes from 'prop-types'

import styles from './document.module.css'

export default function PersonList(props) {
  if (props.entities.length === 0) { return '' }
  const [displayed, setDisplayed] = useState(false);

  // props.entities does contain all references to each entity
  const entities = Object.values(Object.fromEntries(props.entities.map(x => [x.ref.value, x])))
  const attr4entity = e => e.properties.map(({name, value}) => `${name}:${value}`).join(', ')

  return(
    <div>
      <h6 onClick={() => setDisplayed(!displayed)} style={{cursor: 'pointer'}}>
        {props.type[0].toUpperCase() + props.type.slice(1)}s ({entities.length})
        <div className='d-inline ml-1'>
          <i className={styles.hovered + (displayed === true ? ' d-none' : ' fas fa-chevron-right')}></i>
          <i className={displayed === false ? 'd-none' : 'fas fa-chevron-down'}></i>
        </div>
      </h6>
      <ul className={displayed === false ? 'd-none' : ''}>
        {entities.map(e => 
          <li key={e.ref.value}>
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