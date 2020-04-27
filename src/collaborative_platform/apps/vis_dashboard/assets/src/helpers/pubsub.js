/* Module: PubSubChannel
 * Implementation of the Publisher/Subscriber pattern.
 *
 * After a channel is created, adding an object to the channel
 * will result in the object having the publish and subscribe
 * methods available.
 * */

export default function PubSubService () {
  let subscriptions = {}

  function _nextSubscriptionId (channel) {
    let nextId = 0
    if (Object.hasOwnProperty.call(subscriptions, channel)) {
      const subscriptionIds = Object.keys(subscriptions[channel])
      if (subscriptionIds.length > 0) {
        nextId = +subscriptionIds[subscriptionIds.length - 1] + 1
      }
    }
    return nextId
  }

  function _suscribe (channel, callback) {
    const subId = _nextSubscriptionId(channel)

    if (!Object.hasOwnProperty.call(subscriptions, channel)) { subscriptions[channel] = {} }

    subscriptions[channel][subId] = callback
    return subId
  }

  function _unsubscribe (channel, subId) {
    if (Object.hasOwnProperty.call(subscriptions, channel) &&
      Object.hasOwnProperty.call(subscriptions[channel], subId)) {
      delete subscriptions[channel][subId]
    }
    return subId
  }

  function _publish (channel, args) {
    if (Object.hasOwnProperty.call(subscriptions, channel)) { Object.values(subscriptions[channel]).forEach(a => a(args)) }
  }

  function _addToChannel (obj) {
    obj.subscribe = _suscribe
    obj.unsubscribe = _unsubscribe
    obj.publish = _publish
  }

  function _reset () {
    subscriptions = {}
  }

  function _getSubscribers () {
    for (const channel of Object.entries(subscriptions)) {
      console.info(`Event: ${channel[0]} Subscribed: ${Object.keys(channel[1]).length}`)
    }
  }

  return {
    reset: _reset,
    getSubscribers: _getSubscribers,
    register: _addToChannel,
    publish: _publish
  }
}
