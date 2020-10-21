import React from 'react'
import PropTypes from 'prop-types'

import { TEIentities, SelectionType } from 'common/types'
import xml from 'common/helpers/xml.js'
import { AppContext } from 'common/context/app'
import websocket from 'common/helpers/websocket_api'
import { Document } from 'components/document'
import { Tooltip } from 'components/tooltip'
import { Header } from 'components/header'
import styles from './app.module.css' // eslint-disable-line no-unused-vars
import defState from './def_state.js'

export default class App extends React.Component {
  constructor (props) {
    super(props)

    const { projectId, user, fileId, fileName, configuration } = props

    TEIentities.update(configuration.properties_per_entity)
    this.socket = websocket.socket(projectId, fileId)
    this.state = defState(
      fileId,
      fileName,
      user,
      configuration,
      this.socket
    )

    this.onHover = this.onHover.bind(this)
    this.onHoverOut = this.onHoverOut.bind(this)
    this.onClick = this.onClick.bind(this)
    this.onClickOut = this.onClickOut.bind(this)
    this.onSelection = this.onSelection.bind(this)
    this.handleWebsocketResponse = this.handleWebsocketResponse.bind(this)

    this.socket.addCallback('onload', this.handleWebsocketResponse)
    this.socket.addCallback('onreload', this.handleWebsocketResponse)
  }

  componentDidMount () {
    this.socket.connect()
  }

  sendToWebsocket (json) {
    this.socket.send(json)
  }

  handleWebsocketResponse (response) {
    // validate response
    this.setState(prev => {
      const newState = Object.assign({}, prev)
      newState.documentContent = response.body_content
      newState.context.authors = response.authors
      newState.context.annotations = response.certainties
      newState.context.operations = response.operations
      newState.fileVersion = '' + response.file_version
      newState.selection = null

      const entities = Object
        .values(response.entities_lists)
        .reduce((ac, dc) => [...ac, ...dc], [])

      newState.context.entities = xml.processEntitiesInDocument(
        response.body_content,
        entities,
        response.certainties,
        prev.context.configuration.properties_per_entity)

      console.log(newState.context.entities, response)

      return newState
    })
  }

  onSelection (selection) {
    // console.log('selection', selection)
    this.setState({ selection })
  }

  onHover (selection) {
    // console.log('hover', selection)
    this.setState({ selection })
  }

  onHoverOut () {
    this.setState(prev => {
      if (prev.selection === null) { return prev }
      if (prev.selection.type !== SelectionType.hover) { return prev }
      const newState = Object.assign({}, prev, { selection: null })
      return newState
    })
  }

  onClick (selection) {
    // console.log('hover', selection)
    this.setState({ selection })
  }

  onClickOut () {
    this.setState(prev => {
      if (prev.selection === null) { return prev }
      if (prev.selection.type === SelectionType.click ||
        prev.selection.type === SelectionType.textSelection) {
        const newState = Object.assign({}, prev, { selection: null })
        return newState
      }
      return prev
    })
  }

  render () {
    return (
      <AppContext.Provider value={this.state.context}>
        <div className={styles.app + ' container-lg px-lg-5'}>
          <Header
            fileName={this.state.fileName}
            fileId={this.state.fileId}
            fileVersion={this.state.fileVersion}
          />
          <Document
            documentContent={this.state.documentContent}
            onHover={this.onHover}
            onHoverOut={this.onHoverOut}
            onClick={this.onClick}
            onClickOut={this.onClickOut}
            onSelection={this.onSelection}
          />
        </div>
        <Tooltip selection={this.state.selection}/>
      </AppContext.Provider>
    )
  }
}

App.propTypes = {
  savedConf: PropTypes.object,
  projectId: PropTypes.string,
  user: PropTypes.string,
  fileId: PropTypes.string,
  fileName: PropTypes.string,
  configuration: PropTypes.object
}
