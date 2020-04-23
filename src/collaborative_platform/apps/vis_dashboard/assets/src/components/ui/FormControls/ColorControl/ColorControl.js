import React from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'

export default function ColorControl ({ name, value = '#fff', onValueChange, params }) {
  const handleChange = e => onValueChange(e.target.value)

  function createLabel (name) {
    const separated = name.replace(/[A-Z]/g, x => ' ' + x)
    const capitalized = separated[0].toUpperCase() + separated.slice(1).toLowerCase()
    return capitalized
  }

  return (
    <div className={styles.colorControl}>
      <div className={'form-group ' + styles.formGroupOverride}>
        <label htmlFor={'input-' + name}>{createLabel(name)}</label>
        <input
          value={value}
          onChange={handleChange}
          type="color"
          className="form-control"
          id={'input-' + name} />
      </div>
    </div>
  )
}

ColorControl.propTypes = {
  name: PropTypes.string,
  value: PropTypes.string,
  onValueChange: PropTypes.func,
  params: PropTypes.object
}
