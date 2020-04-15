import DataService from './dataservice';
import Filter from './filter';
import Subscription from './subscription';


window.dataClient = DataClient();

/**
  * class DataClient
  * Components interact with an instance of this class
  * which has a reference to the instance of the Data
  * class.
  */
export default function DataClient(){
	const self = {};

	function _init(){
		self._filters = {}; // saved by dimension
		self._subscriptions = {}; // saved by source

		self.subscribe = _subscribe;
		self.unsubscribe = _unsubscribe;
		self.filter = _filter;
		self.unfilter = _unfilter;
		self.focusDocument = _focus;
		self.getFilters = _getFilters;
		self.getSubscriptions = _getSubscriptions;

		return self;
	}

	function _getFilters(){
		return Object.keys(self._filters);
	}

	function _getSubscriptions(){
		return Object.keys(self._subscriptions);
	}

	/**
	 * _subscribe
	 * @param dim
	    *      
	 */
	function _subscribe(source, callable){
		if(!self._subscriptions.hasOwnProperty(source)){
			const subscription = DataService.subscribe(source, callable);

			if(subscription == null)
				throw('Could not subscribe to source: '+source);
			self._subscriptions[source] = subscription;
		}else{
			console.info('Attempted to re-subscribe to source: '+source);
		}
	}

	/**
	 * _unsubscribe
	 * @param sub
	 *      
	 */
	function _unsubscribe(source){
		if(self._subscriptions.hasOwnProperty(source)){
			DataService.unsubscribe(self._subscriptions[source]);
			delete self._subscriptions[source];
		}else{
			console.info('Attempted to unsubscribe from an unfollowed source: '+source);
		}
	}

	/**
	 * Receives a Filter instance and returns a copy of the Filter
	 * with the
	 */
	function _filter(dim, filterFunc){
		if(self._filters.hasOwnProperty(dim))
			DataService.unfilter(self._filters[dim]);

		const filter = DataService.filter(dim, filterFunc);

		if(filter == null)
			throw('Could not filter by dimension: '+dim);
		self._filters[dim] = filter;
	}

	/**
	 * 
	 */
	function _unfilter(dim){
	  	if(self._filters.hasOwnProperty(dim)){
	  		DataService.unfilter((self._filters[dim]));
			delete self._filters[dim];
		}else{
			console.info('Attempted to unfilter an already unfiltered dimension: '+dim);
		}
	}

	/**
	 * Receives a document id.
	 */
	function _focus(documentId){
		DataService.focusDocument(documentId);
	}

	return _init();
}