import React, {useState, useEffect} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import { Navigation } from 'components/navigation'
import { Body } from 'components/body'
import { SaveButton } from 'components/saveButton'


const buffSize = 5

function useProposalIds(projectId) {
  const [ids, setIds] = useState([])

  useEffect(() => {
    updateProposalIds(projectId, setIds)
  }, [])
  return [ids, () => updateProposalIds(projectId, setIds)]
}

function updateProposalIds(projectId, setIds) {
  API.getProposalList(projectId)
  .then(ids => {
    setIds(ids)
  })
  .catch(err => console.error('Failed to update proposal ids for project ' + projectId, err))
}

function useProposalDetails(projectId, listIndex, focusedIndex, ids, proposals, setFocused) {
  useEffect(() => {
    updateProposalDetails(projectId, listIndex, focusedIndex, ids, proposals, setFocused)
  }, [ids, focusedIndex])
}

function updateProposalDetails(projectId, listIndex, focusedIndex, ids, proposals, setFocused) {
  if ((proposals.length === 0) || (listIndex > focusedIndex) || (listIndex+buffSize < focusedIndex)) {
    if (focusedIndex >= ids.length) {return}
    API.getProposalDetails(projectId, {ids:ids[focusedIndex]}, {})
    .then(details => {
      setFocused(details[0])
    })
    .catch(err => console.error('Failed to update proposal details for project ' + projectId))
    //setFocused(details[focusedIndex])

  } else {
    setFocused(proposals[focusedIndex % buffSize])
  }
}

function useProposalList(projectId, listIndex, ids, setProposals) {
  useEffect(() => {
    updateProposalList(projectId, listIndex, ids, setProposals)
  }, [listIndex, ids])
}

function updateProposalList(projectId, listIndex, ids, setProposals) {
  const ids2fetch = ids.slice(listIndex, listIndex+buffSize)
  if (ids2fetch.length === 0) {return}

  const idQueryParameter = ids2fetch.join('&ids=')
  API.getProposalDetails(projectId, {ids:idQueryParameter}, {})
  .then(details => {
    setProposals(details.sort((a,b) => ids2fetch.indexOf(a.id) - ids2fetch.indexOf(b.id)))
  })
  .catch(err => console.error('Failed to retrieve proposal list for project ' + projectId))
}

export default function Unifications ({projectId, configuration}) {
  const [ids, updateIds] = useProposalIds(projectId)
  const [focusedIndex, setFocusedIndex] = useState(0)
  const [focused, setFocused] = useState(null)
  const [proposals, setProposals] = useState([])
  const [listIndex, setListIndex] = useState(0)
  const [unsavedOperations, setUnsavedOperations] = useState([])

  useProposalIds(projectId)
  useProposalList(projectId, listIndex, ids, setProposals)
  useProposalDetails(projectId, listIndex, focusedIndex, ids, proposals, setFocused)

  const refresh = () => {
    if (focusedIndex === ids.length - 1) {
      setFocusedIndex(focusedIndex+1)
    }
    updateProposalIds(projectId, newIds => {
      updateProposalList(projectId, listIndex, newIds, setProposals)
      updateProposalDetails(projectId, listIndex, focusedIndex, newIds, [], setFocused)
      updateIds()
    })
  }

  return (
    <div>
      <SaveButton {...{projectId, unsavedOperations}}/>
      <Navigation {...{
        proposals,
        listIndex,
        buffSize,
        ids,
        setListIndex,
        focusedIndex,
        configuration,
        setFocusedIndex}}/>
      <Body {...{focused, refresh, projectId, configuration}}/>
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
