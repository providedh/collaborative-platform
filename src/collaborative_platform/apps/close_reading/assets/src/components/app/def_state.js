export default function defState (fileId, fileName, fileVersion, user, configuration, websocket) {
  return {
    fileId,
    fileName,
    fileVersion,
    documentContent: '',

    selection: null,

    context: {
      user,
      configuration,
      websocket,
      authors: [],
      annotations: [],
      entities: {}
    }
  }
}
