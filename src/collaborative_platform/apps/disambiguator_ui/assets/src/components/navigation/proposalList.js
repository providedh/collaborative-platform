import React, {useState} from 'react'
import PropTypes from 'prop-types'

import styles from './styles.module.css' // eslint-disable-line no-unused-vars
import {EntityName, CliqueName} from 'common/components'

export default function ProposalList ({
    listShown,
    proposals,
    listIndex,
    buffSize,
    ids,
    setListIndex,
    focusedIndex,
    configuration,
    setFocusedIndex}) {
  const listCssClasses = [
    'card',
    'shadow',
    styles.proposalList,
    listShown === false ? 'd-none' : ''
  ].join(' ')

  const proposalEntries = proposals.map((p, i) => {
    const {target_entity, target_clique} = p
    const targetIsClique = target_entity === undefined && target_clique !== undefined
    const cssClasses = [
      styles.proposalEntry,
      ids[focusedIndex] === p.id ? styles.listEntryFocused : ''
    ].join(' ')
    return <div
        onClick={() => setFocusedIndex(listIndex + i)}
        key={i}
        className={cssClasses}>
      <EntityName entity={p.entity} configuration={configuration}/>
      <p className={styles.updownArrow}>⇳</p>
      {targetIsClique === false
        ?<EntityName entity={target_entity} configuration={configuration}/>
        :<CliqueName clique={target_clique} configuration={configuration}/>}
    </div>
  })

  return (
  <div className={styles.listContainer}>
    <div className={listCssClasses}>
      <div className="card-body">
        {proposalEntries}
        <div className={styles.listPagination}>
          <button
              onClick={() => setListIndex(Math.max(0, listIndex-buffSize))}
              type="button"
              className="btn btn-link">
            <p className="d-inline m-0 p-0"></p> <span>⟵</span>
          </button>
          <span>{listIndex + 1}-{listIndex + proposals.length + 1} / {ids.length}</span>
          <button
              onClick={() => setListIndex(Math.min(buffSize * Math.trunc(ids.length / buffSize), listIndex+buffSize))}
              type="button"
              className="btn btn-link">
            <p className="d-inline m-0 p-0"></p> <span>⟶</span>
          </button>
        </div>
      </div>
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
