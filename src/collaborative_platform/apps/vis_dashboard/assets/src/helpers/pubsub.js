/* Module: PubSubChannel
 * Implementation of the Publisher/Subscriber pattern.
 *
 * After a channel is created, adding an object to the channel
 * will result in the object having the publish and subscribe
 * methods available.
 * */

export default function PubSubService(){
	let subscriptions = {};

	function _nextSubscriptionId(channel){
		let nextId = 0;
		if(subscriptions.hasOwnProperty(channel)){
			const subscriptionIds = Object.keys(subscriptions[channel]);
			if(subscriptionIds.length > 0){
				nextId = +subscriptionIds[subscriptionIds.length - 1] + 1;
			}
		}
		return nextId;
	}

	function _suscribe(channel, callback){
		const subId = _nextSubscriptionId(channel);

		if(!subscriptions.hasOwnProperty(channel))
			subscriptions[channel] = {};

		subscriptions[channel][subId] = callback;
		return subId;
	}

	function _unsubscribe(channel, subId){
		if(subscriptions.hasOwnProperty(channel) && 
		   		subscriptions[channel].hasOwnProperty(subId)){
			delete subscriptions[channel][subId];
		}
		return subId;
	}

	function _publish(channel, args){
		if(subscriptions.hasOwnProperty(channel))
			Object.values(subscriptions[channel]).forEach(a=>a(args));
	}

	function _addToChannel(obj){
		obj.subscribe = _suscribe;
		obj.unsubscribe = _unsubscribe;
		obj.publish = _publish;
	}

	function _reset(){
		subscriptions = {};
	}

	function _getSubscribers(){
		for(let channel of Object.entries(subscriptions)){
			console.info(`Event: ${channel[0]} Subscribed: ${Object.keys(channel[1]).length}`);
		}
	}

	return {
		reset: _reset,
		getSubscribers: _getSubscribers,
		register: _addToChannel,
		publish: _publish
	}
}