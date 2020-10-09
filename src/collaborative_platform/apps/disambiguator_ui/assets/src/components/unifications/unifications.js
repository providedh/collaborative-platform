import React, {useState, useEffect} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import { Header } from 'components/header'
import { Navigation } from 'components/navigation'
import { Body } from 'components/body'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars
    import details from './details.json'


const buffSize = 5

function useProposalIds(projectId) {
  const [ids, setIds] = useState([])
  useEffect(() => {
    API.getProposalList(projectId)
    .then(ids => {
      setIds('2'.repeat(details.length).split('').map(x => +x))
      //setIds(ids);
    })
    .catch(err => console.error('Failed to retrieve proposal ids for project ' + projectId))
  }, [])
  return ids;
}

function useProposalDetails(projectId, listIndex, focusedIndex, ids, proposals, setFocused) {
  useEffect(() => {
    if ((proposals.length === 0) || (listIndex > focusedIndex) || (listIndex+buffSize < focusedIndex)) {
      // fetch the ids[focusedIndex] item
      setFocused(details[focusedIndex])      

    } else {
      setFocused(proposals[focusedIndex % buffSize])
    }
  }, [focusedIndex])
}

function useProposalList(projectId, listIndex, ids, setProposals) {
  useEffect(() => {
    // fetch the ids[listIndex : listIndex + buffSize] items
    setProposals(details.slice(listIndex, listIndex + buffSize))      
  }, [listIndex])
}

export default function Unifications ({projectId, configuration}) {
  const ids = useProposalIds(projectId)
  const [focusedIndex, setFocusedIndex] = useState(0)
  const [focused, setFocused] = useState(null)
  const [proposals, setProposals] = useState([])
  const [listIndex, setListIndex] = useState(0)
  
  useProposalIds(projectId)
  useProposalDetails(projectId, listIndex, focusedIndex, ids, proposals, setFocused)
  useProposalList(projectId, listIndex, ids, setProposals)

  return (
    <div>
      <Navigation {...{
        proposals,
        listIndex,
        buffSize,
        ids,
        setListIndex,
        focusedIndex,
        configuration,
        setFocusedIndex}}/>
      <Body {...{focused, projectId, configuration}}/>
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
