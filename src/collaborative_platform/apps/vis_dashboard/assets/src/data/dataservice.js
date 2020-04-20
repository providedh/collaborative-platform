import {EntityDataSource, CertaintyDataSource, DocumentDataSource, StatsDataSource, MetaDataSource} from './datasources';
import {PubSubService} from '../helpers';
import Filter from './filter';
import Subscription from './subscription';

/**
  * class DataService
  * Manage filters and source subsciptions.
  * 
  * Holds the instance of the publication and subscription
  * service used for broadcasting data filtering and updates.
  * 
  * Filter ids are created automaically, while subscription ids
  * are generated by the pub/sub service.
  */
export default (function DataService(){
	const self = {};

	function _init(){
	
		self._filters = {};		
		// Create pub/sub service and add itself to 
		self._pubSubService = PubSubService();
		self._pubSubClient = {};
		self._pubSubService.register(self._pubSubClient);
		self._context = null;
		self._sources = {};		

		self.setAppContext = _setContext;
		self.subscribe = _subscribe;
		self.unsubscribe = _unsubscribe;
		self.filter = _filter;
		self.unfilter = _unfilter;
		self.focusDocument = _focus;
		self.subscribeToStatus = _subscribeToStatus;

		return self;
	}

	function _setContext(context){
		self._context = context;

		self._sources = {
			meta: MetaDataSource(self._pubSubService, context),
			stats: StatsDataSource(self._pubSubService, context),
			certainty: CertaintyDataSource(self._pubSubService, context),
			entity: EntityDataSource(self._pubSubService, context),
			document: DocumentDataSource(self._pubSubService, context),
		}	
	}

	function _subscribeToStatus(callable){
		return self._pubSubClient.subscribe('status', callable);
	}

	/**
	 * _subscribe
	 * @param dim
	    *      
	 */
	function _subscribe(source, callable){
		if(!self._sources.hasOwnProperty(source))
			throw('Data source not found: '+source);

	  	const channel = 'data/'+source,
	  		subId = self._pubSubClient.subscribe(channel, callable),
	  		sub = Subscription(channel, subId);

	  	callable(self._sources[source].get());
	  	return sub;
	}

	/**
	 * _unsubscribe
	 * @param sub
	    *      
	 */
	function _unsubscribe(sub){
		self._pubSubClient.unsubscribe(sub.channel, sub.id);
	}

	/**
	 * _nextFilterId
	 * @param dim
	 *      
	 */
	function _nextFilterId(dim){
		let nextId = 0;
		if(self._filters.hasOwnProperty(dim)){
			const filterIds = Object.keys(self._filters[dim]);
			if(filterIds.length > 0){
				nextId = +filterIds[filterIds.length - 1] + 1;
			}
		}
		return nextId;
	}

	/**
	 * Receives a Filter instance and returns a copy of the Filter
	 * with the
	 */
	function _filter(dim, filterFunc){
		const filterId = _nextFilterId(dim),
			filter = Filter(dim, filterId, filterFunc);

		if(!self._filters.hasOwnProperty(dim))
			self._filters[dim] = {};

		self._filters[dim][filterId] = filterFunc;

		_applyFilters4Dim(dim);
		return filter;
	}

	/**
	 * 
	 */
	function _unfilter(filter){
	  	if(self._filters.hasOwnProperty(filter.dim) && 
		   		self._filters[filter.dim].hasOwnProperty(filter.id)){
			delete self._filters[filter.dim][filter.id];
		}

		_applyFilters4Dim(filter.dim)
		return filter;
	}

	/**
	 * 
	 * @param dim
	    *      
	 */
	function _createDimFilter(dim){
		const filters = Object.values(self._filters[dim]),
			filterFunc = data=>filters.reduce((ac, dc)=>ac && dc(data), data);
		if(filters.length === 0){
			return null;
		}else{
			return filterFunc;
		}
	}

	/**
	 * message = 'filter/' + dim
	 * 
	 * @param dim
	    *      
	 */
	function _applyFilters4Dim(dim){
		const filter = _createDimFilter(dim);
		self._pubSubClient.publish('filter/'+dim, {dim, filter});
	}

	function _focus(documentId){
		self._pubSubClient.publish('focus/document', {documentId})
	}

	return _init();
})()