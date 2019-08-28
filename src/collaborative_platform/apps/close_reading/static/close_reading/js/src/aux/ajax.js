/* Module: AjaxCalls
 * Module for building full API call urls.
 *
 * API endpoints:
 * - get_save_url
 * - get_add_annotation_url
 * - get_history_url
 * - get_autocomplete_url
 * */
var AjaxCalls = function(args){
	const base_url = [window.location.protocol + '/', window.location.hostname+':5000', 'api/v1'].join('/');

	const save_url = (project, file) => ['project', project, 'teiclose', file, 'save/'].join('/');
	const annotate_url = (project, file) => ['project', project, 'teiclose', file, 'annotate/'].join('/');
	const history_url = (project, file, version) => ['project', project, 'teiclose', file, version, 'annotationhistory/'].join('/');
	const search_url = (project, entity_type, query) => ['fuzzysearch', project, entity_type, query].join('/');

	function _init(args){
		const obj = {
			get_save_url: (project, file) => base_url + '/' + save_url(project, file),
			get_add_annotation_url: (project, file) => base_url + '/' + annotate_url(project, file),
			get_history_url: (project, file, version) => base_url + '/' + history_url(project, file, version),
			get_autocomplete_url: (project, entity_type, query) => base_url + '/' + search_url(project, entity_type, query)
		};

		return obj;
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default AjaxCalls;
