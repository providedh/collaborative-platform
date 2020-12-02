import React from 'react'
import PropTypes from 'prop-types'

import { TEIentities, SelectionType } from 'common/types'
import xml from 'common/helpers/xml.js'
import { AppContext } from 'common/context/app'
import websocket from 'common/helpers/websocket_api'
import parseAnnotation from 'common/helpers/annotationParse'
import { Document } from 'components/document'
import { Tooltip } from 'components/tooltip'
import { Header } from 'components/header'
import styles from './app.module.css' // eslint-disable-line no-unused-vars
import defState from './def_state.js'

export default class App extends React.Component {
  constructor (props) {
    super(props)

    const { projectId, user, fileId, fileName, configuration } = props
    configuration.entities['text fragment'] = {color: 'grey', icon: '', listable: false}
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
    this.handleContentUpdate = this.handleContentUpdate.bind(this)
    this.handleUsersUpdate = this.handleUsersUpdate.bind(this)
    this.pushToast = this.pushToast.bind(this)
    this.popToast = this.popToast.bind(this)
    this.removeToast = this.removeToast.bind(this)

    this.socket.addCallback('onload', this.handleWebsocketResponse)
    this.socket.addCallback('onreload', this.handleWebsocketResponse)
  }

  componentDidMount () {
    this.socket.connect()
  }

  sendToWebsocket (json) {
    this.socket.send(json)
  }

  pushToast(ok, title, content) {
    this.setState(prev => {
      const id = setTimeout(() => this.popToast(), 3500)

      const newState = Object.assign({}, prev)
      newState.toasts.push({id, ok, title, content})

      return newState
    })
  }

  popToast() {
    this.setState(prev => {
      const newState = Object.assign({}, prev)

      const toast = newState.toasts.splice(0,1)
      clearTimeout(toast.id)

      return newState
    })
  }

  removeToast(id) {
    this.setState(prev => {
      const newState = Object.assign({}, prev)

      const toastIndex = newState.toasts
        .map((x, i) => ({i, ...x}))
        .reduce((ac, dc) => ac > -1 ? ac : (dc.id === id ? dc.i : -1), -1)
      const toast = newState.toasts.splice(toastIndex,1)
      clearTimeout(id)

      return newState
    })
  }

  handleWebsocketResponse (response) {
    if (response.ok === false) {
      this.pushToast(false, 'Error', 'There was an error handling the request.')
      console.error('Non-valid websoket message.')
      console.error(response)
    } else if (response.type === 'content'){
      this.handleContentUpdate (response)
    } else if (response.type === 'users'){
      this.handleUsersUpdate (response)
    }
  }

  handleUsersUpdate (response) {
    this.setState({users: response.connected_users})
  }

  handleContentUpdate (response) {
    this.setState(prev => {
      const newState = Object.assign({}, prev)
      newState.documentContent = response.body_content
      newState.context.authors = response.authors
      newState.context.annotations = response.certainties.map(parseAnnotation)
      newState.context.operations = response.operations
      newState.fileVersion = '' + response.file_version
      newState.selection = null

      const entities = Object
        .values(response.entities_lists)
        .reduce((ac, dc) => [...ac, ...dc], [])

      newState.context.entities = xml.processEntitiesInDocument(
        response.body_content,
        entities,
        response.certainties.map(parseAnnotation),
        prev.context.configuration.properties_per_entity)

      return newState
    })
    this.pushToast(true, 'Refreshed', 'The content just updated.')
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

  getToasts() {
    return <div className={styles.toasts}>
      {this.state.toasts.map(t =>
            <div key={t.id} className="toast show" role="alert" aria-live="assertive" aria-atomic="true">
              <div className="toast-header">
                <svg
                  className="bd-placeholder-img rounded mr-2"
                  width="20"
                  height="20"
                  xmlns="http://www.w3.org/2000/svg"
                  preserveAspectRatio="xMidYMid slice"
                  focusable="false"
                  role="img">
                    <rect width="100%" height="100%" fill={t.ok === true ? '#007aff' : '#8e133b'}></rect>
                </svg>
                <strong className="mr-auto">{t.title}</strong>
                <small className="text-muted"></small>
                <button
                  onClick={() => this.removeToast(t.id)}
                  type="button" className="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div className="toast-body">
                {t.content}
              </div>
            </div>)}
    </div>
  }

  render () {
    return (
      <AppContext.Provider value={this.state.context}>
        <div className={styles.app + ' container-lg px-lg-5'}>
          {this.getToasts()}
          <Header
            fileName={this.state.fileName}
            fileId={this.state.fileId}
            fileVersion={this.state.fileVersion}
            users={this.state.users}
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
