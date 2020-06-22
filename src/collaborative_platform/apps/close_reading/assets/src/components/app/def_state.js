export default function defState(fileId, fileName, fileVersion, user, configuration) {
  return {
    fileId,
    fileName,
    fileVersion,
    documentContent: '',

    selection: null,

    context: {
        user,
        authors: [],
        annotations: [],
        entities: [],
        configuration: configuration
    },
  }
}