import crossfilter from 'crossfilter2';

import {AjaxCalls} from '../../helpers';

/* Class: CertaintyDataSource
 *
 * 
 * */
export default function CertaintyDataSource(pubSubService, appContext){
	const self = {};

	function _init(pubSubService, appContext){
		self._sourceName = 'certainty';

	 	self._data = crossfilter([]);
	 	self._textDimension = self._data.dimension(x=>x.textContext);

	 	self._appContext = appContext
		
		/**
		 * Method for retrieving data.
		 */
		self._source = AjaxCalls();

		/**
		* This options allow recreating the state.
		* They are used to query for the data and take into
		* account applied filters.
		*/
		self._options = {};

		self._fetched = false;

		self.get = _getData;

		pubSubService.register(self);

		//self.subscribe(`filter/entityId`, args=>_filterDimension(self._idDimension, args.filter));
		//self.subscribe(`filter/entityName`, args=>_filterDimension(self._nameDimension, args.filter));
		//self.subscribe(`filter/entityType`, args=>_filterDimension(self._typeDimension, args.filter));
		//self.subscribe(`filter/fileName`, args=>_filterDimension(self._docNameDimension, args.filter));
		//self.subscribe(`filter/fileId`, args=>_filterDimension(self._docIdDimension, args.filter));

		return self;
	}

	function _publishData(){
		const data = {all:self._data.all(), filtered:self._data.allFiltered()};
		self.publish(`data/${self._sourceName}`, data);
	}

	function _handleAction(args){
		_filter(args.dim, args.filter)
	}

	function _getData(){
		if(self._fetched === false){
			self._fetched = true;
			_retrieve();
		}
		return({all:self._data.all(), filtered:self._data.allFiltered()});
	}

	/**
	 * Handles filtering for the selected dimension. Depending on the dimension
	 * and type of filtering, this will be done through crossfiltering or by retrieving
	 * data with query parameters.
	 * 
	 * If new data is retrieved, crossfilter filters must be preserved.
	 * 
	 * If the filtering function is null, then the filter is deleted.
	 * 
	 * @param dimension
	 *      
	 * @param args
	 *      
	 */
	function _filterDimension(dimension, filter){
		dimension.filterFunction(filter);
		_publishData();
	}

	function _processData(data){
		const annotations = [];
		
		for(let entity of data){
			const attributes = entity.attributes != null
				?entity.attributes.map(x=>[x.name, x.value])
				:[];

			if(entity.uncertainties == null)
				entity.uncertainties = [null];

			annotations.push(...entity.uncertainties.map(u=>Object.fromEntries([
				...attributes,
				['tag', entity.tag],
				['textContext', entity.textContext]
				])));
		}

		return annotations;
	}

	/**
	 * Retrieves data from the external source.
	 */
	function _retrieve(){
		const files = Object.keys(self._appContext.id2document);
		let retrieved = 0, retrieving = files.length;

		self.publish('status',{action:'fetching'});
		files.forEach(file=>{
			self._data.remove(()=>true); // clear previous data

			self._source.getAnnotations({project:self._appContext.project, file},{},null).then(response=>{
				if(response.success === false)
					console.info('Failed to retrieve entities for file: '+file);
				else{
					//console.log(response.content)
					self._data.add(_processData(response.content));
					_publishData();
				}
				if(++retrieved == retrieving){
					self.publish('status',{action:'fetched'});
				}
			});
		});
	}

	return _init(pubSubService, appContext);
}