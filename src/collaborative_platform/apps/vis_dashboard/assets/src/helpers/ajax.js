import $ from 'jquery';
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
	const base_url = [window.location.protocol + '/', window.location.hostname+':'+window.location.port].join('/');

	// VIS DASHBOARD
	const update_url = ({project, dashboard}) => ['/dashboard', 'project', project, 'vis', dashboard, 'update'].join('/');

	// STATS
	const stats_entities = ({project}) => ['/api', 'stats', 'projects', project, 'entities'].join('/');
	const stats_attributes = ({project}) => ['/api', 'stats', 'projects', project, 'entities', 'attributes'].join('/');
	const stats_documents = ({project}) => ['/api', 'stats', 'projects', project, 'documents'].join('/');

	// CLOSE READING
	const close_history = ({project, file, version}) => ['/api', 'close_reading', 'project', project, 'file', file, 'version', version, 'history'].join('/');
	const fuzzysearch = ({project, entity, query}) => ['/fuzzysearch', 'fuzzysearch', project, entity, query].join('/');

	// API VIS
	const vis_cliques = ({project}) => ['/api', 'vis', 'projects', project, 'cliques'].join('/');
	const vis_cliques_file = ({project, file}) => ['/api', 'vis', 'projects', project, 'files', file, 'cliques'].join('/');
	const vis_entities = ({project}) => ['/api', 'vis', 'projects', project, 'entities'].join('/');
	const vis_entities_file = ({project, file}) => ['/api', 'vis', 'projects', project, 'files', file, 'entities'].join('/');
	const vis_entities_unbound = ({project}) => ['/api', 'vis', 'projects', project, 'entities', 'unbounded_entities'].join('/');
	const vis_entities_unbound_file = ({project, file}) => ['/api', 'vis', 'projects', project, 'files', file, 'entities', 'unbounded_entities'].join('/');

	const vis_projects = ({}) => ['/api', 'vis', 'projects'].join('/');
	const vis_history = ({project}) => ['/api', 'vis', 'projects', project, 'history'].join('/');
	const vis_files = ({project}) => ['/api', 'vis', 'projects', project, 'files'].join('/');
	const vis_file = ({project, file}) => ['/api', 'vis', 'projects', project, 'files', file].join('/');
	const vis_file_meta = ({project, file}) => ['/api', 'vis', 'projects', project, 'files', file, 'meta'].join('/');
	const vis_annotations = ({project, file}) => ['/api', 'vis', 'projects', project, 'files', file, 'annotations'].join('/');
	const vis_context = ({project, query}) => ['/api', 'vis', 'projects', project, 'context', query].join('/');

	function _init(args){
		const obj = {
			// VIS DASHBOARD
			updateDashboard: (options,params,data) => _createCall('POST', _createUrl(update_url, options, params), data),

			// STATS
			getStatEntities: (options, params, data) => _createCall('GET', _createUrl(stats_entities, options, params), data),
			getStatsAttributes: (options, params, data) => _createCall('GET', _createUrl(stats_attributes, options, params), data),
			getStatsDocuments: (options, params, data) => _createCall('GET', _createUrl(stats_documents, options, params), data),

			// CLOSE READING
			getFileHistory: (options, params, data) => _createCall('GET', _createUrl(close_history, options, params), data),
			fuzzysearch: (options, params, data) => _createCall('GET', _createUrl(fuzzysearch, options, params), data),

			// API VIS
			getCliques: (options, params, data) => _createCall('GET', _createUrl(vis_cliques, options, params), data),
			getFileCliques: (options, params, data) => _createCall('GET', _createUrl(vis_cliques_file, options, params), data),
			getEntities: (options, params, data) => _createCall('GET', _createUrl(vis_entities, options, params), data),
			getFileEntities: (options, params, data) => _createCall('GET', _createUrl(vis_entities_file, options, params), data),
			getUnboundEntities: (options, params, data) => _createCall('GET', _createUrl(vis_entities_unbound, options, params), data),
			getFileUnboundEntities: (options, params, data) => _createCall('GET', _createUrl(vis_entities_unbound_file, options, params), data),

			getProjects: (options, params, data) => _createCall('GET', _createUrl(vis_projects, options, params), data),
			getHistory: (options, params, data) => _createCall('GET', _createUrl(vis_history, options, params), data),
			getFiles: (options, params, data) => _createCall('GET', _createUrl(vis_files, options, params), data),
			getFile: (options, params, data) => _createCall('GET', _createUrl(vis_file, options, params), data),
			getFileMeta: (options, params, data) => _createCall('GET', _createUrl(vis_file_meta, options, params), data),
			getAnnotations: (options, params, data) => _createCall('GET', _createUrl(vis_annotations, options, params), data),
			getSearchContext: (options, params, data) => _createCall('GET', _createUrl(vis_context, options, params), data),
		};

		return obj;
	}

	function _createUrl(resource, options, params){
		const paramsString = Object.entries(params).map(([key, value])=>`?${key}=${value}`).join('');
		const url = base_url + resource(options) + paramsString + '/';
		return url;
	}

	function _createCall(method,url,data={}){
		function getCookie(name) {
		    let cookieValue = null;
		    if (document.cookie && document.cookie !== '') {
		        const cookies = document.cookie.split(';');
		        for (let i = 0; i < cookies.length; i++) {
		            const cookie = cookies[i].trim();
		            // Does this cookie string begin with the name we want?
		            if (cookie.substring(0, name.length + 1) === (name + '=')) {
		                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		                break;
		            }
		        }
		    }
		    return cookieValue;
		}

		const csrftoken = getCookie('csrftoken');

		return new Promise(function(resolve, cancel){
			function csrfSafeMethod(method) {
			    // these HTTP methods do not require CSRF protection
			    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
			}

			$.ajaxSetup({
			    beforeSend: function(xhr, settings) {
			        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
			            xhr.setRequestHeader("X-CSRFToken", csrftoken);
			        }
			    }
			});

			$.ajax({
		        url: url,
		        type: method,   //type is any HTTP method
		        data: data,      //Data as js object
		        statusCode: {
					304: function() {
				      resolve({success:false, content:'Not Modified.'});
				    },
				    202: function() {
				      resolve({success:false, content:'Request Accepted But Not Completed.'});
				    },
				    200: function(a) {
				      resolve({success:true, content:a});
				    }
				},
		        error: function (a) {
		            resolve({success:false, content:a});
		        }
		    })
		})
	}

	function _notimplemented(method){
		return function(){throw(new Error('Not implemented : '+method))};
	}

	return _init(args);
};

export default AjaxCalls;
