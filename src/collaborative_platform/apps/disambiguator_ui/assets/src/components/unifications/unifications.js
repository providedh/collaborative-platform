import React, {useState, useEffect} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import { Header } from 'components/header'
import { Navigation } from 'components/navigation'
import { Body } from 'components/body'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

const buffSize = 10

function useProposalIds(projectId) {
  const [ids, setIds] = useState([])
  useEffect(() => {
    API.getProposalList(projectId)
    .then(ids => {
      setIds(ids);
    })
    .catch(err => console.error('Failed to retrieve proposal ids for project ' + projectId))
  }, [])
  return ids;
}

function useProposalDetails(projectId, listIndex, focusedIndex, proposalIds, proposals, setFocused) {
  useEffect(() => {
    if ((proposals.length === 0) || (listIndex > focusedIndex) || (listIndex+buffSize < focusedIndex)) {
      // fetch the proposalIds[focusedIndex] item
    } else {
      setFocused(proposals[focusedIndex % buffSize])
    }
  }, focusedIndex)
}

function useProposalList(projectId, listIndex, proposalIds, setProposals) {
  useEffect(() => {
    // fetch the proposalIds[listIndex : listIndex + buffSize] items
  }, listIndex)
}

export default function Unifications ({projectName, projectId, projectVersion, ...restProps}) {
  const ids = useProposalIds(projectId)
  const [focusedIndex, setFocusedIndex] = useState(0)
  const [focused, setFocused] = useState(null)
  const [proposals, setProposals] = useState([])
  const [listIndex, setListIndex] = useState(0)

  return (
    <div>
      <Navigation {...{proposals, listIndex, setListIndex, focusedIndex, setFocusedIndex}}/>
      <Body focused={focused}/>
    </div>
  )
}

Unifications.propTypes = {
  savedConf: PropTypes.object,
  projectId: PropTypes.string,
  user: PropTypes.string,
  projectId: PropTypes.string,
  projectName: PropTypes.string,
  projectVersion: PropTypes.string,
  configuration: PropTypes.object
}
