import {AjaxCalls} from '../../helpers';

/* Class: EntityDataSource
 *
 * 
 * */
export default function EntityDataSource(pubSubService, project){
	const self = {};

	function _init(pubSubService, project){
		self._sourceName = 'entity';
	 	self._data = null;
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

		self.get = ()=>self._data;

		pubSubService.register(self);
		self.subscribe(`filter/xdim`, _handleAction);

		return self;
	}

	function _publishData(data){
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
	function _filter(dimension, filter){
		const filtered = self._data.filter(x=>filter(x[1]));
		_publishData(filtered);
	}

	/**
	 * Retrieves data from the external source.
	 */
	function _retrieve(){
		self._source.getFiles({project:self._project},{},null).then(files=>{
			files.forEach(file=>{
				self._source.getFileEntities({project:self._project, file:file.id},{},null).then(entities=>{
					console.log(entities);
				});
			})
		})
		self._data = Object.entries({a:1, b:2, c:4, d:5, e:6, f:7});
	}

	return _init(pubSubService, project);
}