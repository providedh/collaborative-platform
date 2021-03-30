export default function defState (fileId, fileName, user, configuration, websocket) {
  return {
    fileId,
    fileName,
    fileVersion: '',
    documentContent: '',
    toasts: [],
    users: [],

    selection: null,

    context: {
      user,
      configuration,
      websocket,
      authors: [],
      annotations: [],
      entities: [],
      operations: []
    }
  }
}
