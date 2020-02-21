/* Class: Filter
 *
 * Represents a single filter applied to data dimension.
 * 
 * */
export default function Filter(dim, id){
	function _init(dim, id){
		const self = {dim, id};
		
		self.toString = ()=>JSON.stringify({dim, id})

		return self;
	}

	return _init(dim, id);
}

Filter.prototype.fromString = function(json){
	let filter = null;
	try{
		const {dim, id} = JSON.parse(json);
		filter = Filter(dim, id);
	}catch{
		throw('Not able to parse json :'+json);
	}

	return filter;
}