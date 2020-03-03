/* Class: Subscription
 *
 * Represents a single subsciption to a publish/subscribe service channel.
 * 
 * */
export default function Subscription(channel, id){
	function _init(channel, id){
		self = {channel, id};
		
		self.toString = ()=>JSON.stringify({channel, id})

		return self;
	}

	return _init(channel, id);
}

Subscription.prototype.fromString = function(json){
	let filter = null;
	try{
		const {channel, id} = JSON.parse(json);
		filter = Subscription(channel, id);
	}catch{
		throw('Not able to parse json :'+json);
	}

	return filter;
}