export default ({config}) => {
  return {
    extra: {
      "serverUrl": process.env.AR_CP_SERVER_URL || config.serverUrl
    }
  }
}
