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
      setIds(ids)
    })
    .catch(err => console.error('Failed to retrieve proposal ids for project ' + projectId))
  }, [])
  return ids;
}

function useProposalDetails(projectId, listIndex, focusedIndex, ids, proposals, setFocused) {
  useEffect(() => {
    if ((proposals.length === 0) || (listIndex > focusedIndex) || (listIndex+buffSize < focusedIndex)) {
      if (focusedIndex >= ids.length) {return}
      API.getProposalDetails(projectId, {ids:ids[focusedIndex]}, {})
      .then(details => {
        setFocused(details[0])
      })
      .catch(err => console.error('Failed to retrieve proposal details for project ' + projectId))
      //setFocused(details[focusedIndex])

    } else {
      setFocused(proposals[focusedIndex % buffSize])
    }
  }, [ids, focusedIndex])
}

function useProposalList(projectId, listIndex, ids, setProposals) {
  useEffect(() => {
    const ids2fetch = ids.slice(listIndex, listIndex+buffSize)
    if (ids2fetch.length === 0) {return}

    const idQueryParameter = ids2fetch.join('&ids=')
    API.getProposalDetails(projectId, {ids:idQueryParameter}, {})
    .then(details => {
      setProposals(details.sort((a,b) => ids2fetch.indexOf(a.id) - ids2fetch.indexOf(b.id)))
    })
    .catch(err => console.error('Failed to retrieve proposal ids for project ' + projectId))
    //setProposals(details.slice(listIndex, listIndex + buffSize))      
  }, [listIndex, ids])
}

export default function Unifications ({projectId, configuration}) {
  const ids = useProposalIds(projectId)
  const [focusedIndex, _setFocusedIndex] = useState(0)
  const [focused, setFocused] = useState(null)
  const [proposals, setProposals] = useState([])
  const [listIndex, setListIndex] = useState(0)
  
  const setFocusedIndex = (i) => {
    console.log('setting idx', i)
    _setFocusedIndex(i)
  }
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
