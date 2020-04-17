import crossfilter from 'crossfilter2';

import {AjaxCalls} from '../../helpers';

/* Class: MetaDataSource
 *
 * 
 * */
export default function MetaDataSource(pubSubService, appContext){
	const self = {};

	function _init(pubSubService, appContext){
		self._sourceName = 'meta';

	 	self._data = crossfilter([]);
	 	self._fileIdDimension = self._data.dimension(x=>x.file);

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
		self.subscribe(`filter/fileId`, args=>_filterDimension(self._fileIdDimension, args.filter));

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

	function _createEntry(obj, parent){
	    const [attr_name, attr_value] = Object.entries(obj)[0];
	    return Object.fromEntries([
	        [`${parent}_${attr_name}`,attr_value]
	    ]);
	}

	function _getEntries(obj){
		if(obj == null)
			return [];

		return Object.entries(obj)
			.filter(x=>!typeof(x) != 'string')
			.filter(x=>x[0] != 'classCode' || !x[1].hasOwnProperty('certainty'))
	    	.filter(x=>x[0].startsWith('@') || typeof(x[1]) != 'string' || x[0] == '#text'); 
	}

	function _processData(obj, file){
	    const pool = [_getEntries(obj)], entities = [];
	    
	    while(pool.length > 0){
	        const current = pool.shift(); // [[key, value]]
	        
	        current.forEach(([attrName, attrValue])=>{
	            if(Array.isArray(attrValue)){
	                pool.push(...attrValue.map(x=>_getEntries(x)))
	            }else if(attrName.startsWith('@')){
	                if(attrValue.length > 0)
	                    entities.push([attrName, attrValue])
	                else{
	                	const value = current.filter(x=>x[0]=='#text');
	                	if(value.length == 1)
		                    entities.push([
		                        attrName,
		                        value[0][1]
		                    ])
	                }
	            }else{
	                pool.push(_getEntries(attrValue))
	            }
	        });
	    }
	    
	    return([{file, entities}]);
	}

	/**
	 * Retrieves data from the external source.
	 */
	function _retrieve(){
		self.publish('status',{action:'fetching'});
		self._source.getFiles({project:self._appContext.project},{},null).then(response=>{
			if(response.success === false)
				throw('Failed to retrieve files for the current project.')
			
			let retrieved = 0, retrieving = response.content.length;
			response.content.forEach(file=>{
				self._data.remove(()=>true); // clear previous data

				self._source.getFileMeta({project:self._appContext.project, file:file.id},{},null).then(response=>{
					if(response.success === false)
						console.info('Failed to retrieve meta information for file: '+file.id);
					else{
						self._data.add(_processData(response.content, file.id));
						_publishData();
					}
					if(++retrieved == retrieving){
						self.publish('status',{action:'fetched'});
					}
				});
			})
		})
	}

	return _init(pubSubService, appContext);
}