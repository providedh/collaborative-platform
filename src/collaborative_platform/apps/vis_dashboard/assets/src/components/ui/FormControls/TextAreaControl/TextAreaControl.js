import React from 'react'
import PropTypes from 'prop-types'

import styles from './style.module.css'

export default function TextAreaControl ({ name, value = '', onValueChange, params }) {
  const placeholder = Object.hasOwnProperty.call(params, 'placeholder')
    ? params.placeholder
    : ''

  const jsonSafeText = text => text.replace(/\n/g, '\\n')
  const originalText = text => text.replace(/\\n/g, '\n')

  function handleChange (e) {
    const contents = e.target.value
    onValueChange(jsonSafeText(contents))
  }

  function createLabel (name) {
    const separated = name.replace(/[A-Z]/g, x => ' ' + x)
    const capitalized = separated[0].toUpperCase() + separated.slice(1).toLowerCase()
    return capitalized
  }

  return (
    <div className={styles.textControl}>
      <div className={'form-group ' + styles.formGroupOverride}>
        <label htmlFor={'input-' + name}>{createLabel(name)}</label>
        <textarea placeholder={placeholder} className="form-control" value={originalText(value)} onChange={handleChange}/>
      </div>
    </div>
  )
}

TextAreaControl.propTypes = {
  name: PropTypes.string,
  value: PropTypes.string,
  onValueChange: PropTypes.func,
  params: PropTypes.object
}
