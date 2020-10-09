import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars

export default function ProposalList ({proposals, listIndex, buffSize, ids, setListIndex, focusedIndex, setFocusedIndex}) {
  const listCssClasses = [
    'card',
    styles.proposalList
  ].join(' ')
  return (
  <div className={listCssClasses}>
    <div className="card-body">
      This is some text within a card body.
    </div>
  </div>)
}

ProposalList.propTypes = {
  proposals: PropTypes.arrayOf(PropTypes.object),
  listIndex: PropTypes.number,
  setListIndex: PropTypes.func,
  focusedIndex: PropTypes.number,
  setFocusedIndex: PropTypes.func,
}
