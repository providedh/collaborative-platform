import crossfilter from 'crossfilter2';

import {AjaxCalls} from '../../helpers';

/* Class: EntityDataSource
 *
 * 
 * */
export default function EntityDataSource(pubSubService, project){
	const self = {};

	function _init(pubSubService, project){
		self._sourceName = 'entity';

	 	self._data = crossfilter([]);
	 	self._idDimension = self._data.dimension(x=>x.id);
	 	self._nameDimension = self._data.dimension(x=>x.name);
	 	self._typeDimension = self._data.dimension(x=>x.type);

	 	self._project = project
		
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

		_retrieve();

		self.get = ()=>({all:self._data.all(), filtered:self._data.allFiltered()});

		pubSubService.register(self);

		self.subscribe(`filter/id`, args=>_filterDimension(self._idDimension, args.filter));
		self.subscribe(`filter/name`, args=>_filterDimension(self._nameDimension, args.filter));
		self.subscribe(`filter/type`, args=>_filterDimension(self._typeDimension, args.filter));

		return self;
	}

	function _publishData(){
		const data = {all:self._data.all(), filtered:self._data.allFiltered()};
		self.publish(`data/${self._sourceName}`, data);
	}

	function _handleAction(args){
		_filter(args.dim, args.filter)
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

	/**
	 * Retrieves data from the external source.
	 */
	function _retrieve(){
		self._source.getFiles({project:self._project},{},null).then(response=>{
			if(response.success === false)
				throw('Failed to retrieve files for the current project.')
			
			response.content.forEach(file=>{
				self._data.remove(()=>true); // clear previous data
				let retrieved = 0;

				self._source.getFileEntities({project:self._project, file:file.id},{},null).then(response=>{
					if(response.success === false)
						console.info('Failed to retrieve entities for file: '+file.id);
					else
						self._data.add(response.content);
					
					if(++retrieved == response.content.length)
						_publishData();
				});
			})
		})
	}

	return _init(pubSubService, project);
}