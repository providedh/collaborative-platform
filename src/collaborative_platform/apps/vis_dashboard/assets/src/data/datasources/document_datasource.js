import {AjaxCalls} from '../../helpers';

const dummyDocument = {getElementsByTagName: ()=>[{innerHTML: ''}]}

/* Class: DocumentDatasource
 *
 * 
 * */
export default function DocumentDataSource(pubSubService, project){
	const self = {};

	function _init(pubSubService, project){
		self._sourceName = 'document';
	 	self._project = project
		
		/**
		 * Method for retrieving data.
		 */
		self._source = AjaxCalls();
		self._focused = '';
		self._document = dummyDocument;
		self._projectVersion = 'latest';

		self.get = _getData;

		pubSubService.register(self);

		self.subscribe(`focus/document`, ({documentId})=>_focusDocument(documentId));
		
		return self;
	}

	function _publishData(){
		const data = {contents: self._document};
		self.publish(`data/${self._sourceName}`, data);
	}

	function _getData(){
		return({contents: self._document});
	}

	function _focusDocument(documentId){
		self._focused = documentId;
		_retrieve();
	}

	/**
	 * Retrieves data from the external source.
	 */
	function _retrieve(){
		self._source.getFile({project:self._project, file:self._focused},{},null).then(response=>{
			if(response.success === false)
				throw('Failed to retrieve files for the current project.')
			
			self._document = response.content;
			_publishData();
		})
	}

	return _init(pubSubService, project);
}