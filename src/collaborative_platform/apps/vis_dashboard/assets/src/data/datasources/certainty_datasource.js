import crossfilter from 'crossfilter2';

import {AjaxCalls} from '../../helpers';

/* Class: CertaintyDataSource
 *
 * 
 * */
export default function CertaintyDataSource(pubSubService, project){
	const self = {};

	function _init(pubSubService, project){
		self._sourceName = 'entity';

	 	self._data = crossfilter([]);
	 	self._textDimension = self._data.dimension(x=>x.textContext);

	 	self._project = project
		
		/**
		 * Method for retrieving data.
		 */
		self._source = AjaxCalls();
		console.log(self._source)
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
		self.publish('status',{action:'fetching'});
		self._source.getFiles({project:self._project},{},null).then(response=>{
			if(response.success === false)
				throw('Failed to retrieve files for the current project.')
			
			let retrieved = 0, retrieving = response.content.length;
			response.content.forEach(file=>{
				self._data.remove(()=>true); // clear previous data

				self._source.getAnnotations({project:self._project, file:file.id},{},null).then(response=>{
					if(response.success === false)
						console.info('Failed to retrieve entities for file: '+file.id);
					else{
						console.log(_processData(response.content))
						self._data.add(_processData(response.content));
						_publishData();
					}
					if(++retrieved == retrieving){
						self.publish('status',{action:'fetched'});
					}
				});
			})
		})
	}

	return _init(pubSubService, project);
}