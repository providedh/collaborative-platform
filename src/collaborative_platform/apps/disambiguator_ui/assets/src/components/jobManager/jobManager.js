import React, {useState} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

export default function Jobs ({currentIndex, unifications, ...restProps}) {
  window.API = API
  return (<div className={styles.jobs}></div>)
}

Jobs.propTypes = {
  currentIndex: PropTypes.number,
  unifications: PropTypes.arrayOf(PropTypes.object),
}
