import React, {useState, useEffect} from 'react'
import PropTypes from 'prop-types'

import {API} from 'common/helpers'
import { Header } from 'components/header'
import { Navigation } from 'components/navigation'
import { Body } from 'components/body'
import styles from './styles.module.css' // eslint-disable-line no-unused-vars

const unificationBufferSize = 10

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

export default function Unifications ({projectName, projectId, projectVersion, ...restProps}) {
  const ids = useProposalIds(projectId)
  const [unifications, updateUnifications] = useState([])
  const [currentIndex, setIndex] = useState(0)

  return (
    <div>
      <Navigation {...{unifications, currentIndex, setIndex}}/>
      <Body {...{unifications, currentIndex}}/>
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
