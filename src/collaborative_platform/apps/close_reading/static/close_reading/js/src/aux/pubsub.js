/* Module: PubSubChannel
 * Implementation of the Publisher/Subscriber pattern.
 *
 * After a channel is created, adding an object to the channel
 * will result in the object having the publish and subscribe
 * methods available.
 * */

var Channel = function(){
	let subscribers = {};

	function _suscribe(event, callback){
		if(subscribers.hasOwnProperty(event))
			subscribers[event].push(callback);
		else
			subscribers[event] = [callback,];
	}

	function _publish(event, args){
		if(subscribers.hasOwnProperty(event))
			subscribers[event].forEach(a=>a(args));
	}

	function _addToChannel(obj){
		obj.subscribe = _suscribe;
		obj.publish = _publish;
	}

	function _reset(){
		subscribers = {};
	}

	function _getSubscribers(){
		for(let event of Object.entries(subscribers))
			console.info(`Event: ${event[0]} Subscribed: ${len(event[1])}`);
	}

	return {
		reset: _reset,
		getSubscribers: _getSubscribers,
		addToChannel: _addToChannel
	}
}

var PubSubChannel = (function(){
	const someHiddenPar = 23;

	function _print(){
		console.log(someHiddenPar);
	}

	return {
		version: 1,
		create: Channel,
		imprime: _print
	}
})()

export default PubSubChannel;
