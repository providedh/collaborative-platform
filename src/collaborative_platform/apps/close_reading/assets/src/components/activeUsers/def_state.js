export default function defState (fileId, fileName, user, configuration, websocket) {
  return {
    fileId,
    fileName,
    fileVersion: '',
    documentContent: '',
    toasts: [],

    selection: null,

    context: {
      user,
      users: [],
      configuration,
      websocket,
      authors: [],
      annotations: [],
      entities: [],
      operations: []
    }
  }
}
